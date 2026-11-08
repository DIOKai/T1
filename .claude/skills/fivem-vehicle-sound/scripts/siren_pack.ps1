<#
.SYNOPSIS
  Build (or dump) a FiveM server-side siren sound pack with CodeWalker.Core (free, local).

.DESCRIPTION
  build : WAV folders -> a ready resource:
            <Out>\<pack>\dlc_<pack>\<bank>.awc          one wave bank per folder (e.g. federal, state, county, city)
            <Out>\<pack>\data\<pack>_sounds.dat54.rel   SimpleSound per WAV + one SoundSet per bank
            <Out>\<pack>\data\<pack>_sounds.dat54.nametable, fxmanifest.lua, client.lua (loads the banks), TONES.txt
          Input layout:  <WavRoot>\<bank>\<TONE>.wav   (mono, 16-bit PCM; any sample rate CodeWalker accepts)
          Names:  SoundSet  <PREFIX>_SIRENS_<BANK>      (what Renewed-Sirensync / PlaySoundFromEntity calls the audioRef)
                  sound     <PREFIX>_<CODE>_<TONE>      (the audioName; CODE = bank name or -BankCodes mapping)
                  stream    lowercase sound name inside <bank>.awc
          All names are written to the REL in lowercase: CodeWalker hashes names case-sensitively, but the game lowercases
          audio names before hashing (vanilla dat54 only holds lowercase-name hashes), so an uppercase REL plays nothing.
          Every stream loops from the start (LoopPoint 0) — what a siren needs. SimpleSound header copied from the
          vanilla siren sounds (flags 0x0020E000, category vehicles_sirens). SoundSet entries are sorted by name hash
          (the game looks them up by binary search; CodeWalker also sorts on import — verified).
  dump  : write an existing pack's dat54 + every bank's streams as XML + WAVs (read-only on the source). The REL holds
          only name hashes: pass -NamesFile (e.g. a TONES.txt or a siren controller config) to see names as text.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File siren_pack.ps1 build -CodeWalker "D:\Tools\CodeWalker" -WavRoot "D:\work\sirens" -Pack lore_sirens -Prefix LORE -BankCodes "federal=FED" -Out "D:\work\out"
  powershell -ExecutionPolicy Bypass -File siren_pack.ps1 dump  -CodeWalker "D:\Tools\CodeWalker" -Res "D:\server\resources\lore_sirens" -Out "D:\work\dump"
#>
param(
    [Parameter(Mandatory = $true, Position = 0)][ValidateSet('build', 'dump')][string]$Command,
    [Parameter(Mandatory = $true)][string]$CodeWalker,
    [string]$WavRoot,
    [string]$Pack,
    [string]$Prefix,
    [string]$BankCodes = '',          # e.g. "federal=FED,state=STATE"
    [string]$Res,
    [string]$NamesFile,               # dump: TONES.txt (or any text) listing sound / SoundSet names to resolve hashes
    [Parameter(Mandatory = $true)][string]$Out,
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
$dll = Join-Path $CodeWalker 'CodeWalker.Core.dll'
if (-not (Test-Path $dll)) { throw "CodeWalker.Core.dll not found in $CodeWalker" }
$asm = [Reflection.Assembly]::LoadFrom($dll)

function Hash29([string]$s) { [CodeWalker.GameFiles.JenkHash]::GenHash($s.ToLowerInvariant()) -band 0x1FFFFFFF }
function Hash32([string]$s) { [uint32][CodeWalker.GameFiles.JenkHash]::GenHash($s.ToLowerInvariant()) }
function New-Entry([string]$n) { $e = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.RpfBinaryFileEntry')); $e.Name = $n; $e.NameLower = $n.ToLowerInvariant(); $e }
function Read-Wav([string]$path) {
    $b = [IO.File]::ReadAllBytes($path)
    if ([Text.Encoding]::ASCII.GetString($b, 0, 4) -ne 'RIFF') { throw "$path is not a WAV" }
    $i = 12; $info = @{ path = $path }
    while ($i + 8 -le $b.Length) {
        $id = [Text.Encoding]::ASCII.GetString($b, $i, 4); $len = [BitConverter]::ToUInt32($b, $i + 4)
        if ($id -eq 'fmt ') { $info.fmt = [BitConverter]::ToUInt16($b, $i + 8); $info.ch = [BitConverter]::ToUInt16($b, $i + 10); $info.rate = [BitConverter]::ToUInt32($b, $i + 12); $info.bits = [BitConverter]::ToUInt16($b, $i + 22) }
        elseif ($id -eq 'data') { $info.dataOff = $i + 8; $info.dataLen = [int]$len; break }
        $i += 8 + $len + ($len % 2)
    }
    if ($info.fmt -ne 1 -or $info.ch -ne 1 -or $info.bits -ne 16) {
        throw "$path must be mono 16-bit PCM (got fmt $($info.fmt), $($info.ch) ch, $($info.bits) bit). Convert: ffmpeg -i in.wav -ac 1 -c:a pcm_s16le out.wav"
    }
    $info.frames = [int]($info.dataLen / 2); $info.bytes = $b; $info
}
function Write-MonoWav([string]$path, [int]$rate, [byte[]]$pcm) {
    $ms = New-Object IO.MemoryStream; $bw = New-Object IO.BinaryWriter($ms)
    $bw.Write([Text.Encoding]::ASCII.GetBytes('RIFF')); $bw.Write([uint32](36 + $pcm.Length)); $bw.Write([Text.Encoding]::ASCII.GetBytes('WAVEfmt '))
    $bw.Write([uint32]16); $bw.Write([uint16]1); $bw.Write([uint16]1); $bw.Write([uint32]$rate); $bw.Write([uint32]($rate * 2)); $bw.Write([uint16]2); $bw.Write([uint16]16)
    $bw.Write([Text.Encoding]::ASCII.GetBytes('data')); $bw.Write([uint32]$pcm.Length); $bw.Write($pcm); $bw.Flush()
    [IO.File]::WriteAllBytes($path, $ms.ToArray())
}

if ($Command -eq 'dump') {
    if (-not $Res) { throw '-Res is required' }
    # REL files store only hashes of names; resolve them from a names list if you have one (packs built by this tool ship TONES.txt)
    if ($NamesFile) { foreach ($w in [Regex]::Matches((Get-Content -Raw $NamesFile), '[A-Za-z0-9_]{3,}')) { $null = [CodeWalker.GameFiles.JenkIndex]::Ensure($w.Value.ToLowerInvariant()) } }
    elseif (Test-Path (Join-Path $Res 'TONES.txt')) { foreach ($w in [Regex]::Matches((Get-Content -Raw (Join-Path $Res 'TONES.txt')), '[A-Za-z0-9_]{3,}')) { $null = [CodeWalker.GameFiles.JenkIndex]::Ensure($w.Value.ToLowerInvariant()) } }
    New-Item -ItemType Directory -Force $Out | Out-Null
    $rels = Get-ChildItem -Recurse $Res -Filter *.dat54.rel
    foreach ($f in $rels) {
        $r = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.RelFile')); $r.Load([IO.File]::ReadAllBytes($f.FullName), (New-Entry $f.Name))
        $x = [CodeWalker.GameFiles.RelXml]::GetXml($r)
        # register the script names so the lowercase stream names resolve in the AWC dump
        foreach ($m in [Regex]::Matches($x, '<ScriptName>([^<]+)</ScriptName>')) { $null = [CodeWalker.GameFiles.JenkIndex]::Ensure($m.Groups[1].Value.ToLowerInvariant()) }
        [IO.File]::WriteAllText((Join-Path $Out "$($f.Name).xml"), $x); "dumped $($f.Name)"
    }
    foreach ($f in Get-ChildItem -Recurse $Res -Filter *.awc) {
        $w = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.AwcFile')); $w.Load([IO.File]::ReadAllBytes($f.FullName), (New-Entry $f.Name))
        $wf = Join-Path $Out $f.BaseName; New-Item -ItemType Directory -Force $wf | Out-Null
        [IO.File]::WriteAllText((Join-Path $Out "$($f.Name).xml"), [CodeWalker.GameFiles.AwcXml]::GetXml($w, $wf)); "dumped $($f.Name) -> $wf"
    }
    return
}

# ---------------- build ----------------
if (-not $WavRoot -or -not $Pack -or -not $Prefix) { throw 'build needs -WavRoot, -Pack and -Prefix' }
$Pack = $Pack.ToLowerInvariant(); $Prefix = $Prefix.ToUpperInvariant()
if ($Pack -notmatch '^[a-z0-9_]{1,24}$') { throw '-Pack: lowercase letters, digits, _ (max 24)' }
$codes = @{}; foreach ($kv in ($BankCodes -split ',' | Where-Object { $_ })) { $k, $v = $kv -split '=', 2; $codes[$k.Trim().ToLowerInvariant()] = $v.Trim().ToUpperInvariant() }
$dest = Join-Path $Out $Pack
if ((Test-Path $dest) -and -not $Force) { throw "$dest exists (use -Force)" }
New-Item -ItemType Directory -Force (Join-Path $dest "dlc_$Pack"), (Join-Path $dest 'data') | Out-Null
$banks = Get-ChildItem $WavRoot -Directory | Sort-Object Name
if (-not $banks) { throw "no bank folders in $WavRoot (expected <WavRoot>\<bank>\<TONE>.wav)" }

$sounds = New-Object Text.StringBuilder; $sets = New-Object Text.StringBuilder; $containers = @(); $tones = @(); $usedNames = @{}
foreach ($bank in $banks) {
    $b = $bank.Name.ToLowerInvariant()
    if ($b -notmatch '^[a-z0-9_]+$') { throw "bank folder '$($bank.Name)': lowercase letters, digits, _ only" }
    $code = if ($codes.ContainsKey($b)) { $codes[$b] } else { $b.ToUpperInvariant() }
    $container = "dlc_$Pack/$b"; $containers += $container
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("siren_" + [Guid]::NewGuid().ToString('N')); New-Item -ItemType Directory $tmp | Out-Null
    try {
        $awcXml = New-Object Text.StringBuilder
        [void]$awcXml.AppendLine('<?xml version="1.0" encoding="UTF-8"?>').AppendLine('<AudioWaveContainer>').AppendLine(' <Version value="1" />').AppendLine(' <ChunkIndices value="True" />').AppendLine(' <Streams>')
        $entries = @()
        foreach ($wav in Get-ChildItem $bank.FullName -Filter *.wav | Sort-Object Name) {
            $tone = ($wav.BaseName -replace '[^A-Za-z0-9_]', '_').ToUpperInvariant()
            $script = "${Prefix}_${code}_${tone}"
            if ($usedNames.ContainsKey($script)) { throw "duplicate sound name $script" }
            $usedNames[$script] = 1
            $stream = $script.ToLowerInvariant()
            $info = Read-Wav $wav.FullName
            $pcm = New-Object byte[] $info.dataLen; [Array]::Copy($info.bytes, $info.dataOff, $pcm, 0, $info.dataLen)
            $frames = $info.frames
            # odd sample counts are fine for plain (unencrypted) PCM banks; padding would add a gap at every loop
            $fileName = ('0x{0:X8}.wav' -f (Hash29 $stream))
            Write-MonoWav (Join-Path $tmp $fileName) $info.rate $pcm
            [void]$awcXml.AppendLine("  <Item>").AppendLine("   <Name>$stream</Name>").AppendLine("   <FileName>$fileName</FileName>").AppendLine('   <Chunks>')
            [void]$awcXml.AppendLine('    <Item>').AppendLine('     <Type>data</Type>').AppendLine('    </Item>')
            [void]$awcXml.AppendLine('    <Item>').AppendLine('     <Type>format</Type>').AppendLine('     <Codec>PCM</Codec>').AppendLine("     <Samples value=""$frames"" />").AppendLine("     <SampleRate value=""$($info.rate)"" />")
            [void]$awcXml.AppendLine('     <Headroom value="0" />').AppendLine('     <PlayBegin value="0" />').AppendLine('     <PlayEnd value="0" />').AppendLine('     <LoopBegin value="0" />').AppendLine('     <LoopEnd value="0" />').AppendLine('     <LoopPoint value="0" />').AppendLine('     <Peak unk="0" />').AppendLine('    </Item>')
            [void]$awcXml.AppendLine('    <Item>').AppendLine('     <Type>peak</Type>').AppendLine('    </Item>').AppendLine('   </Chunks>').AppendLine('  </Item>')
            $snd = "${stream}_snd"
            [void]$sounds.AppendLine('  <Item type="SimpleSound">').AppendLine("   <Name>$snd</Name>").AppendLine('   <Header>').AppendLine('    <Flags value="0x0020E000" />').AppendLine('    <ReleaseTime value="50" />').AppendLine('    <DopplerFactor value="30" />').AppendLine('    <Category>vehicles_sirens</Category>').AppendLine('    <VolumeCurveScale value="300" />').AppendLine('   </Header>')
            [void]$sounds.AppendLine("   <ContainerName>$container</ContainerName>").AppendLine("   <FileName>$stream</FileName>").AppendLine('   <WaveSlotIndex value="0" />').AppendLine('  </Item>')
            $entries += [pscustomobject]@{ Script = $script.ToLowerInvariant(); Sound = $snd; Hash = (Hash32 $script) }
            $tones += ('{0,-34} bank {1,-10} {2,6} Hz {3,8} samples  {4,6:N1} s' -f $script, $b, $info.rate, $frames, ($frames / $info.rate))
        }
        if (-not $entries) { throw "no WAV files in $($bank.FullName)" }
        [void]$awcXml.AppendLine(' </Streams>').AppendLine('</AudioWaveContainer>')
        $doc = New-Object Xml.XmlDocument; $doc.LoadXml($awcXml.ToString())
        $awc = [CodeWalker.GameFiles.XmlAwc]::GetAwc($doc, $tmp)
        [IO.File]::WriteAllBytes((Join-Path $dest "dlc_$Pack\$b.awc"), $awc.Save())
        "bank $b.awc: $($entries.Count) tones"
        # names go into the XML in lowercase: CodeWalker hashes the text as written (case-sensitive), while the game
        # lowercases audio names before hashing (vanilla dat54 only contains lowercase-name hashes; verified 2026-11-08)
        $setName = "${Prefix}_SIRENS_$($b.ToUpperInvariant())".ToLowerInvariant()
        [void]$sets.AppendLine('  <Item type="SoundSet">').AppendLine("   <Name>$setName</Name>").AppendLine('   <Header>').AppendLine('    <Flags value="0xAAAAAAAA" />').AppendLine('   </Header>').AppendLine('   <SoundSets>')
        foreach ($en in ($entries | Sort-Object Hash)) {      # sorted by name hash (CodeWalker re-sorts on import anyway)
            [void]$sets.AppendLine('    <Item>').AppendLine("     <ScriptName>$($en.Script)</ScriptName>").AppendLine("     <ChildSound>$($en.Sound)</ChildSound>").AppendLine('    </Item>')
        }
        [void]$sets.AppendLine('   </SoundSets>').AppendLine('  </Item>')
    } finally { Remove-Item -Recurse -Force $tmp }
}

$rx = New-Object Text.StringBuilder
[void]$rx.AppendLine('<?xml version="1.0" encoding="UTF-8"?>').AppendLine('<Dat54>').AppendLine(' <Version value="7126027" />').AppendLine(' <ContainerPaths>')
foreach ($c in $containers) { [void]$rx.AppendLine("  <Item>$c</Item>") }
[void]$rx.AppendLine(' </ContainerPaths>').AppendLine(' <Items>').Append($sounds.ToString()).Append($sets.ToString()).AppendLine(' </Items>').AppendLine('</Dat54>')
$rdoc = New-Object Xml.XmlDocument; $rdoc.LoadXml($rx.ToString())
$rel = [CodeWalker.GameFiles.XmlRel]::GetRel($rdoc)
[IO.File]::WriteAllBytes((Join-Path $dest "data\${Pack}_sounds.dat54.rel"), $rel.Save())
# self-check: reload and confirm every SoundSet / script name hash equals the game's lowercase hash
$chk = [Activator]::CreateInstance($asm.GetType('CodeWalker.GameFiles.RelFile')); $chk.Load([IO.File]::ReadAllBytes((Join-Path $dest "data\${Pack}_sounds.dat54.rel")), (New-Entry "${Pack}_sounds.dat54.rel"))
$cx = New-Object Xml.XmlDocument; $cx.LoadXml([CodeWalker.GameFiles.RelXml]::GetXml($chk))
$want = @{}; foreach ($n in $rdoc.SelectNodes('//SoundSets/Item/ScriptName') + $rdoc.SelectNodes("//Item[@type='SoundSet']/Name")) { $want['{0:X8}' -f (Hash32 $n.InnerText)] = $n.InnerText }
$got = @(); foreach ($n in $cx.SelectNodes('//SoundSets/Item/ScriptName') + $cx.SelectNodes("//Item[@type='SoundSet']/Name")) { $t = $n.InnerText; $got += $(if ($t -match '^hash_([0-9A-F]{8})$') { $Matches[1] } else { '{0:X8}' -f (Hash32 $t) }) }
$bad = @($got | Where-Object { -not $want.ContainsKey($_) })
if ($bad) { throw "self-check failed: $($bad.Count) names are not lowercase-hashed: $($bad -join ', ')" }
"self-check: $($got.Count) SoundSet/script names hashed in lowercase (as the game looks them up)"
[IO.File]::WriteAllBytes((Join-Path $dest "data\${Pack}_sounds.dat54.nametable"), [Text.Encoding]::ASCII.GetBytes((($containers | ForEach-Object { "$_`0" }) -join '')))

$bankList = ($banks | ForEach-Object { "    'DLC_$($Pack.ToUpperInvariant())\\$($_.Name.ToUpperInvariant())'," }) -join "`n"
[IO.File]::WriteAllText((Join-Path $dest 'fxmanifest.lua'), @"
-- $Pack server-side siren sounds, built with siren_pack.ps1 ($(Get-Date -Format yyyy-MM-dd))
fx_version 'cerulean'
game 'gta5'
lua54 'yes'

files {
    'dlc_$Pack/*.awc',
    'data/${Pack}_sounds.dat54.rel',
    'data/${Pack}_sounds.dat54.nametable',
}

data_file 'AUDIO_WAVEPACK' 'dlc_$Pack'
data_file 'AUDIO_SOUNDDATA' 'data/${Pack}_sounds.dat'

client_script 'client.lua'
"@)
[IO.File]::WriteAllText((Join-Path $dest 'client.lua'), @"
-- Load the siren wave banks so a siren controller can play them (audioRef = ${Prefix}_SIRENS_<BANK>, audioName = see TONES.txt)
local banks = {
$bankList
}

CreateThread(function()
    for _, bank in ipairs(banks) do
        local tries = 0
        while not RequestScriptAudioBank(bank, false) do
            tries = tries + 1
            if tries > 50 then print(('[$Pack] could not load audio bank %s'):format(bank)) break end
            Wait(100)
        end
    end
end)

AddEventHandler('onResourceStop', function(resource)
    if resource ~= GetCurrentResourceName() then return end
    for _, bank in ipairs(banks) do ReleaseNamedScriptAudioBank(bank) end
end)
"@)
[IO.File]::WriteAllLines((Join-Path $dest 'TONES.txt'), @("# audioName (sound)                bank        rate     length", "# audioRef (SoundSet) = ${Prefix}_SIRENS_<BANK>") + $tones)
"wrote $dest  ($($tones.Count) tones in $($banks.Count) banks). Clients must reconnect after installing; restart the server for a first install."
