<#
.SYNOPSIS
  Dump, clone/rename and re-voice GTA V / FiveM add-on engine-sound packs with CodeWalker.Core (free, local).

.DESCRIPTION
  dump   : write every .rel / .awc of a pack as CodeWalker XML (optionally with the WAVs) - read-only on the source.
  clone  : make a new, independent pack <NewName> from an existing engine in a pack: renames the dat151 car item,
           every record the pack itself defines (new unique hashes), the wave-bank container paths and the files,
           writes a new fxmanifest.lua + CREDITS.txt. AWCs are copied byte-for-byte unless -WavDir holds edited WAVs,
           in which case those streams are rebuilt (WAVs must keep the original sample rate, length and mono 16-bit).
  The source folder is never modified.

  Use the SAME CodeWalker build for every XML round trip: CodeWalker renamed most audio fields in 2024, so XML from a
  newer build does not load in an older one (and the other way round).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File sound_pack.ps1 dump  -CodeWalker "D:\Tools\CodeWalker" -Res "D:\packs\tamustanggt50" -Out "D:\work\dump" -Wav
  powershell -ExecutionPolicy Bypass -File sound_pack.ps1 clone -CodeWalker "D:\Tools\CodeWalker" -Res "D:\packs\tamustanggt50" -NewName dominatorgrt -Out "D:\work\out"
  powershell -ExecutionPolicy Bypass -File sound_pack.ps1 clone ... -WavDir "D:\work\edited"   # edited\<awc base name>\<stream>.wav
#>
param(
    [Parameter(Mandatory = $true, Position = 0)][ValidateSet('dump', 'clone')][string]$Command,
    [Parameter(Mandatory = $true)][string]$CodeWalker,      # folder that contains CodeWalker.Core.dll
    [Parameter(Mandatory = $true)][string]$Res,             # pack resource folder (audioconfig\, sfx\)
    [string]$Out,
    [string]$Engine,                                        # engine name inside the pack (default: folder name)
    [string]$NewName,
    [string]$WavDir,
    [switch]$Wav,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
$dll = Join-Path $CodeWalker 'CodeWalker.Core.dll'
if (-not (Test-Path $dll)) { throw "CodeWalker.Core.dll not found in $CodeWalker" }
$asm = [Reflection.Assembly]::LoadFrom($dll)
$Res = (Resolve-Path $Res).Path
if (-not $Engine) { $Engine = Split-Path $Res -Leaf }
$Engine = $Engine.ToLowerInvariant()

$STREAMS = 'engine_accel', 'exhaust_accel', 'engine_decel', 'exhaust_decel', 'engine_idle', 'exhaust_idle'
$SUFFIXES = '', '_engine', '_exhaust', '_engine_accel', '_exhaust_accel', '_granular_engine', '_vehicle_engine',
            '_engine_npc', '_exhaust_npc', '_npc', '_engine_accel_npc', '_exhaust_accel_npc'

function Ensure-Names([string[]]$names) {
    foreach ($n in $names) { if ($n) { $null = [CodeWalker.GameFiles.JenkIndex]::Ensure([string]$n) } }
}
function New-Entry([string]$fileName) {
    $e = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.RpfBinaryFileEntry'))
    $e.Name = $fileName; $e.NameLower = $fileName.ToLowerInvariant(); return $e
}
function Load-Rel([string]$path) {
    $r = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.RelFile'))
    $r.Load([IO.File]::ReadAllBytes($path), (New-Entry (Split-Path $path -Leaf))); return $r
}
function Load-Awc([string]$path) {
    $w = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.AwcFile'))
    $w.Load([IO.File]::ReadAllBytes($path), (New-Entry (Split-Path $path -Leaf))); return $w
}
function Read-WavInfo([string]$path) {
    $br = New-Object IO.BinaryReader([IO.File]::OpenRead($path))
    try {
        if ([Text.Encoding]::ASCII.GetString($br.ReadBytes(4)) -ne 'RIFF') { throw "$path is not a WAV" }
        $null = $br.ReadUInt32(); $null = $br.ReadBytes(4)
        $info = @{}
        while ($br.BaseStream.Position -lt $br.BaseStream.Length) {
            $id = [Text.Encoding]::ASCII.GetString($br.ReadBytes(4)); $len = $br.ReadUInt32()
            if ($id -eq 'fmt ') {
                $info.format = $br.ReadUInt16(); $info.channels = $br.ReadUInt16(); $info.rate = $br.ReadUInt32()
                $null = $br.ReadUInt32(); $null = $br.ReadUInt16(); $info.bits = $br.ReadUInt16()
                if ($len -gt 16) { $null = $br.ReadBytes($len - 16) }
            } elseif ($id -eq 'data') { $info.bytes = $len; break }
            else { $null = $br.ReadBytes($len + ($len % 2)) }
        }
        $info.frames = [int]($info.bytes / [Math]::Max(1, ($info.channels * $info.bits / 8)))
        return $info
    } finally { $br.Close() }
}

# wave-bank container names are stored as hashes of "dlc_<pack>/<bank>" (slash form): register them so the XML shows
# them as text and they can be renamed - otherwise a clone silently keeps playing the source pack's bank
Ensure-Names (@($Engine, "dlc_$Engine", "dlc_$Engine/$Engine", "dlc_$Engine/${Engine}_npc") + ($SUFFIXES | ForEach-Object { "$Engine$_" }) + $STREAMS)
$relFiles = Get-ChildItem -Recurse $Res -Filter *.rel | Where-Object { $_.Name.ToLowerInvariant().StartsWith("${Engine}_") }
$awcFiles = Get-ChildItem -Recurse $Res -Filter *.awc | Where-Object { $_.BaseName.ToLowerInvariant() -in @($Engine, "${Engine}_npc") }
if (-not $relFiles) { throw "no ${Engine}_*.rel under $Res (use -Engine for packs with several engines)" }

if ($Command -eq 'dump') {
    if (-not $Out) { throw '-Out is required' }
    New-Item -ItemType Directory -Force $Out | Out-Null
    foreach ($f in $relFiles) {
        [IO.File]::WriteAllText((Join-Path $Out "$($f.Name).xml"), [CodeWalker.GameFiles.RelXml]::GetXml((Load-Rel $f.FullName)))
        "dumped $($f.Name)"
    }
    foreach ($f in $awcFiles) {
        $wf = ''
        if ($Wav) { $wf = Join-Path $Out $f.BaseName; New-Item -ItemType Directory -Force $wf | Out-Null }
        [IO.File]::WriteAllText((Join-Path $Out "$($f.Name).xml"), [CodeWalker.GameFiles.AwcXml]::GetXml((Load-Awc $f.FullName), $wf))
        "dumped $($f.Name)" + $(if ($Wav) { " + WAVs in $wf" } else { '' })
        if ($Wav) {
            # one line per stream: file, rate, samples, granular? (granular streams must keep rate AND length)
            $ax = New-Object Xml.XmlDocument; $ax.LoadXml((Get-Content -Raw (Join-Path $Out "$($f.Name).xml")))
            $rows = foreach ($st in $ax.SelectNodes('//Streams/Item')) {
                $fn = $st.SelectSingleNode('FileName'); if (-not $fn) { continue }
                $fmt = $st.SelectSingleNode('Chunks/Item[Type="format"]')
                $gran = [bool]$st.SelectSingleNode('Chunks/Item[Type="granulargrains"]')
                '{0,-22} {1,6} Hz {2,8} samples  {3}' -f $fn.InnerText, $fmt.SelectSingleNode('SampleRate').GetAttribute('value'),
                    $fmt.SelectSingleNode('Samples').GetAttribute('value'), $(if ($gran) { 'GRANULAR - keep rate and length' } else { 'one-shot' })
            }
            [IO.File]::WriteAllLines((Join-Path $wf 'streams.txt'), @('# file  rate  length  kind   (0x... names are hashes of one-shot sounds: listen to identify)') + $rows)
            "   $(@($rows).Count) streams, $(@($rows | Where-Object { $_ -match 'GRANULAR' }).Count) granular -> $wf\streams.txt"
        }
    }
    return
}

# ---------------- clone ----------------
if (-not $NewName -or -not $Out) { throw '-NewName and -Out are required for clone' }
$NewName = $NewName.ToLowerInvariant()
if ($NewName -notmatch '^[a-z0-9_]{1,32}$') { throw 'NewName: lowercase letters, digits and _ only' }
if ($NewName -eq $Engine) { throw 'NewName must differ from the source engine name' }
$dest = Join-Path $Out $NewName
if ((Test-Path $dest) -and -not $Force) { throw "$dest exists (use -Force to overwrite)" }
if ((Resolve-Path $Out -ErrorAction SilentlyContinue) -and ((Resolve-Path $Out).Path.StartsWith($Res))) { throw 'Out must be outside the source pack' }
New-Item -ItemType Directory -Force (Join-Path $dest 'audioconfig'), (Join-Path $dest "sfx\dlc_$NewName") | Out-Null

# 1. XML of every rel; collect the names this pack defines
$docs = [ordered]@{}
foreach ($f in $relFiles) {
    $d = New-Object Xml.XmlDocument
    $d.LoadXml([CodeWalker.GameFiles.RelXml]::GetXml((Load-Rel $f.FullName)))
    $docs[$f.Name] = $d
}
$map = @{}
foreach ($d in $docs.Values) {
    foreach ($n in $d.SelectNodes('/*/Items/Item/Name')) {
        $old = $n.InnerText.Trim()
        if (-not $old -or $map.ContainsKey($old.ToLowerInvariant())) { continue }
        if ($old.ToLowerInvariant() -eq $Engine) { $new = $NewName }
        elseif ($old -match '^hash_([0-9A-Fa-f]{8})$') { $new = "${NewName}_$($Matches[1].ToLowerInvariant())" }
        elseif ($old.ToLowerInvariant().Contains($Engine)) { $new = $old.ToLowerInvariant().Replace($Engine, $NewName) }
        else { $new = "${NewName}_$($old.ToLowerInvariant())" }
        $map[$old.ToLowerInvariant()] = $new
    }
}
Ensure-Names ([string[]]$map.Values)
Ensure-Names @("dlc_$NewName/$NewName", "dlc_$NewName/${NewName}_npc")

# 2. rename definitions + references (whole-text matches) and container paths
$containerRx = New-Object Text.RegularExpressions.Regex ("(?i)(dlc_)" + [Regex]::Escape($Engine) + "([\\/])" + [Regex]::Escape($Engine) + "(_npc)?$")
$renamed = 0; $paths = 0
foreach ($d in $docs.Values) {
    foreach ($el in $d.SelectNodes('//*[not(*)]')) {
        $t = $el.InnerText.Trim()
        if (-not $t) { continue }
        $k = $t.ToLowerInvariant()
        if ($map.ContainsKey($k)) { $el.InnerText = $map[$k]; $renamed++; continue }
        if ($containerRx.IsMatch($t)) { $el.InnerText = $containerRx.Replace($t, "`${1}$NewName`${2}$NewName`${3}"); $paths++ }
    }
    # references can also sit in attributes, e.g. RandomizedSound <Variations><Item name="hash_..." value="1"/>
    foreach ($at in $d.SelectNodes('//@*')) {
        $k = $at.Value.Trim().ToLowerInvariant()
        if ($at.Name -ne 'type' -and $map.ContainsKey($k)) { $at.Value = $map[$k]; $renamed++ }
    }
}
$hashLeft = 0
foreach ($d in $docs.Values) { foreach ($el in $d.SelectNodes('//ContainerName')) { if ($el.InnerText -match '^hash_') { $hashLeft++ } } }
if ($hashLeft) { "note: $hashLeft ContainerName values point at other wave banks (vanilla RESIDENT/DLC banks the pack borrows) - left unchanged, which is correct" }
if ($paths -eq 0) { Write-Warning "no wave-bank container path matched dlc_$Engine\$Engine - check the dat54 ContainerPaths" }

# 3. rebuild rel binaries
foreach ($name in $docs.Keys) {
    $newFile = $name.ToLowerInvariant().Replace($Engine, $NewName)
    $rel = [CodeWalker.GameFiles.XmlRel]::GetRel($docs[$name])
    [IO.File]::WriteAllBytes((Join-Path $dest "audioconfig\$newFile"), $rel.Save())
    "rel  $name -> $newFile"
}

# 4. AWCs: copy, or rebuild with edited WAVs
foreach ($f in $awcFiles) {
    $newFile = $f.Name.ToLowerInvariant().Replace($Engine, $NewName)
    $target = Join-Path $dest "sfx\dlc_$NewName\$newFile"
    $edited = if ($WavDir) { Join-Path $WavDir $f.BaseName } else { $null }
    if (-not $edited -or -not (Test-Path $edited)) { Copy-Item $f.FullName $target; "awc  $($f.Name) -> $newFile (copied)"; continue }
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("sndpack_" + [Guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory $tmp | Out-Null
    try {
        $xml = [CodeWalker.GameFiles.AwcXml]::GetXml((Load-Awc $f.FullName), $tmp)
        $n = 0
        foreach ($w in Get-ChildItem $edited -Filter *.wav) {
            $orig = Join-Path $tmp $w.Name
            if (-not (Test-Path $orig)) { throw "$($w.Name): no stream with that file name in $($f.Name) (dump with -Wav to see the names)" }
            $a = Read-WavInfo $orig; $b = Read-WavInfo $w.FullName
            if ($b.format -ne 1 -or $b.channels -ne 1 -or $b.bits -ne 16) { throw "$($w.Name): must be mono 16-bit PCM" }
            if ($b.rate -ne $a.rate -or $b.frames -ne $a.frames) {
                throw "$($w.Name): sample rate/length changed ($($a.rate) Hz/$($a.frames) -> $($b.rate) Hz/$($b.frames)); granular grain tables would break"
            }
            Copy-Item $w.FullName $orig -Force; $n++
        }
        $doc = New-Object Xml.XmlDocument; $doc.LoadXml($xml)
        $awc = [CodeWalker.GameFiles.XmlAwc]::GetAwc($doc, $tmp)
        [IO.File]::WriteAllBytes($target, $awc.Save())
        "awc  $($f.Name) -> $newFile (rebuilt, $n edited WAVs)"
    } finally { Remove-Item -Recurse -Force $tmp }
}

# 5. manifest + credits
$rels = Get-ChildItem (Join-Path $dest 'audioconfig') -Filter *.rel | ForEach-Object { $_.Name }
$types = @{ 'dat151' = 'AUDIO_GAMEDATA'; 'dat54' = 'AUDIO_SOUNDDATA'; 'dat10' = 'AUDIO_SYNTHDATA'; 'dat15' = 'AUDIO_DYNAMIXDATA' }
$lines = @("-- $NewName engine sound, cloned from $Engine with sound_pack.ps1 ($(Get-Date -Format yyyy-MM-dd))",
    "fx_version 'cerulean'", "game 'gta5'", '', 'files {')
$lines += ($rels | ForEach-Object { "    'audioconfig/$_'," })
$lines += (Get-ChildItem (Join-Path $dest "sfx\dlc_$NewName") -Filter *.awc | ForEach-Object { "    'sfx/dlc_$NewName/$($_.Name)'," })
$lines += '}', ''
foreach ($r in ($rels | Sort-Object { if ($_ -match 'dat10') { 0 } else { 1 } })) {
    if ($r -match '^(.*)\.(dat\d+)\.rel$' -and $types.ContainsKey($Matches[2])) {
        $lines += "data_file '$($types[$Matches[2]])' 'audioconfig/$($Matches[1]).dat'"     # path stops at .dat on purpose
    }
}
$lines += "data_file 'AUDIO_WAVEPACK' 'sfx/dlc_$NewName'"
[IO.File]::WriteAllLines((Join-Path $dest 'fxmanifest.lua'), $lines)
[IO.File]::WriteAllLines((Join-Path $dest 'CREDITS.txt'), @(
    "$NewName - cloned from the '$Engine' engine sound pack.",
    "Original pack: <author, URL, licence/permission text - copy it from the pack's readme>",
    "Changes: renamed records and files with sound_pack.ps1" + $(if ($WavDir) { "; edited WAVs from $WavDir" } else { '' }),
    'For use on this server only. Do not re-upload or sell (most packs contain audio the author has no right to license).'))

# 6. verify: reload, names resolved, no source name left
Ensure-Names ([string[]]$map.Values)
$left = @()
foreach ($r in $rels) {
    $x = [CodeWalker.GameFiles.RelXml]::GetXml((Load-Rel (Join-Path $dest "audioconfig\$r")))
    if ($x -match [Regex]::Escape($Engine)) { $left += $r; continue }
    $vd = New-Object Xml.XmlDocument; $vd.LoadXml($x)
    $vals = @($vd.SelectNodes('//*[not(*)]') | ForEach-Object { $_.InnerText.Trim() }) + @($vd.SelectNodes('//@*') | ForEach-Object { $_.Value.Trim() })
    foreach ($v in $vals) {
        $k = $v.ToLowerInvariant()
        if ($map.ContainsKey($k) -and -not ($map.Values -contains $k)) { $left += "$r ($v)"; break }
    }
}
"renamed $($map.Count) records, $renamed references, $paths container paths"
if ($left) { Write-Warning "source name '$Engine' still appears in: $($left -join ', ')" } else { "verify: OK - no '$Engine' left in the new rel files" }
"next: set <audioNameHash>$NewName</audioNameHash> in the car's vehicles.meta, ensure $NewName before the car, reconnect"
