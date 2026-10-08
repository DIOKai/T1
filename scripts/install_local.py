#!/usr/bin/env python3
"""Make T1's skills and rules work in local Claude Code sessions, in any folder.

Cloud sessions and sessions opened inside the T1 folder already pick up
.claude/skills, CLAUDE.md and .claude/settings.json. Local sessions opened in
another folder (your FiveM server, a Blender project...) only read your
user-level ~/.claude. This script links T1 into it:

  1. every skill in .claude/skills -> ~/.claude/skills/<name>
     (a symlink, or a directory junction on Windows, so `git pull` in T1
     updates them; folders you made yourself with the same name are skipped)
  2. a marked block in ~/.claude/CLAUDE.md that imports T1's CLAUDE.md
     (which imports LESSONS.md), so the same rules and lessons apply everywhere
  3. with --plugins: the marketplaces and enabled plugins from
     .claude/settings.json, installed at user scope with the `claude` CLI
  4. with --mcp: the MCP servers from .mcp.json, added at user scope
  5. with --remotion: Remotion's video skills via `npx skills add remotion-dev/skills`
  6. with --auto-update: a user-level SessionStart hook that runs `git pull` in T1 and
     re-links skills each time Claude Code starts (silent unless something changed)
     (not vendored in T1 because that repo has no licence file)
Agents in .claude/agents (impeccable's reviewers) are linked into ~/.claude/agents too.

Usage (from the T1 folder):
    python scripts/install_local.py              # skills + rules
    python scripts/install_local.py --plugins    # + plugins
    python scripts/install_local.py --mcp        # + blender/fivem/freecad/ifc MCP
    python scripts/install_local.py --remotion   # + Remotion video skills (needs Node.js)
    python scripts/install_local.py --auto-update  # keep this computer in sync on every start
    python scripts/install_local.py --all        # everything
    python scripts/install_local.py --dry-run --all
    python scripts/install_local.py --uninstall  # remove links and the block

Re-run after `git pull` to pick up new skills (or use --auto-update).
One-line setup on a new computer: scripts/setup.ps1 (Windows) or scripts/setup.sh. Standard library only.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

T1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME_CLAUDE = os.path.join(os.path.expanduser('~'), '.claude')
USER_SKILLS = os.path.join(HOME_CLAUDE, 'skills')
USER_MEMORY = os.path.join(HOME_CLAUDE, 'CLAUDE.md')
BEGIN, END = '<!-- T1:begin (managed by T1/scripts/install_local.py) -->', '<!-- T1:end -->'
WINDOWS = os.name == 'nt'


USER_SETTINGS = os.path.join(HOME_CLAUDE, 'settings.json')
QUIET = []  # in --update mode, messages are collected here instead of printed


def log(msg):
    if QUIET:
        QUIET.append(msg)
    else:
        print(msg, flush=True)


def is_link(path):
    """True for symlinks and Windows directory junctions."""
    if os.path.islink(path):
        return True
    if hasattr(os.path, 'isjunction') and os.path.isjunction(path):  # Python 3.12+
        return True
    if WINDOWS and os.path.isdir(path):
        try:
            return os.path.realpath(path) != os.path.abspath(path)
        except OSError:
            return False
    return False


def points_into_t1(path):
    try:
        return os.path.realpath(path).startswith(os.path.realpath(T1) + os.sep)
    except OSError:
        return False


def make_link(link, target, dry):
    if dry:
        return True
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except (OSError, NotImplementedError):
        if not WINDOWS:
            raise
    # Windows without Developer Mode can't make symlinks; junctions need no admin rights.
    r = subprocess.run(['cmd', '/c', 'mklink', '/J', link, target], capture_output=True, text=True)
    return r.returncode == 0


def remove_link(path):
    if os.path.islink(path):
        os.unlink(path)
    else:  # junction
        os.rmdir(path)


def sync_skills(dry, uninstall):
    src = os.path.join(T1, '.claude', 'skills')
    names = sorted(n for n in os.listdir(src) if os.path.isfile(os.path.join(src, n, 'SKILL.md')))
    os.makedirs(USER_SKILLS, exist_ok=True)
    added = kept = skipped = removed = 0
    # stale links into T1 (skill deleted or renamed upstream), or everything on uninstall
    for n in os.listdir(USER_SKILLS):
        p = os.path.join(USER_SKILLS, n)
        if is_link(p) and points_into_t1(p) and (uninstall or n not in names or not os.path.exists(p)):
            log(f'  - remove {n}')
            if not dry:
                remove_link(p)
            removed += 1
    if uninstall:
        log(f'skills: removed {removed} links')
        return
    for n in names:
        link, target = os.path.join(USER_SKILLS, n), os.path.join(src, n)
        if os.path.lexists(link):
            if is_link(link) and points_into_t1(link):
                kept += 1
            else:
                log(f'  ! skip {n}: ~/.claude/skills/{n} already exists and is not a T1 link (left untouched)')
                skipped += 1
            continue
        if make_link(link, target, dry):
            log(f'  + link {n}')
            added += 1
        else:
            log(f'  ! could not link {n}')
            skipped += 1
    log(f'skills: {added} added, {kept} already linked, {removed} stale removed, {skipped} skipped')


def block_text():
    t1 = T1.replace('\\', '/')
    return f"""{BEGIN}
# T1 规则（所有本机 Claude Code 会话共用）

T1 仓库位置：`{t1}`。技能已链接到 `~/.claude/skills/`。下面导入 T1 的规则（它再导入 LESSONS.md）：

@{t1}/CLAUDE.md

在 T1 以外的文件夹工作时，用户纠正我就把经验写进 `{t1}/LESSONS.md`，在 T1 仓库里提交（`git -C "{t1}" ...`）。
{END}
"""


USER_AGENTS = os.path.join(HOME_CLAUDE, 'agents')


def sync_agents(dry, uninstall):
    """Link .claude/agents/*.md (e.g. impeccable's reviewers) into ~/.claude/agents."""
    src = os.path.join(T1, '.claude', 'agents')
    names = sorted(n for n in os.listdir(src) if n.endswith('.md')) if os.path.isdir(src) else []
    os.makedirs(USER_AGENTS, exist_ok=True)
    added = removed = skipped = 0
    for n in os.listdir(USER_AGENTS):
        p = os.path.join(USER_AGENTS, n)
        if os.path.islink(p) and points_into_t1(p) and (uninstall or n not in names):
            if not dry:
                os.unlink(p)
            removed += 1
    if not uninstall:
        for n in names:
            link, target = os.path.join(USER_AGENTS, n), os.path.join(src, n)
            if os.path.lexists(link):
                if not (os.path.islink(link) and points_into_t1(link)):
                    log(f'  ! skip agent {n}: already exists and is not a T1 link')
                    skipped += 1
                continue
            if not dry:
                try:
                    os.symlink(target, link)
                except (OSError, NotImplementedError):
                    shutil.copyfile(target, link)  # Windows without Developer Mode: copy (re-run after git pull)
            added += 1
    log(f'agents: {added} added, {removed} removed, {skipped} skipped')


def sync_remotion(dry):
    """Remotion's skills have no licence file, so T1 can't vendor them; install them with Remotion's own command."""
    npx = shutil.which('npx')
    if not npx and not dry:
        log('  ! npx not found: install Node.js, then re-run with --remotion')
        return
    cmd = [npx or 'npx', '-y', 'skills', 'add', 'remotion-dev/skills', '-g', '-a', 'claude-code', '-s', '*', '-y']
    log('  $ ' + ' '.join(cmd))
    if not dry:
        env = dict(os.environ, DO_NOT_TRACK='1', DISABLE_TELEMETRY='1')
        r = subprocess.run(cmd, env=env)
        log('remotion: installed into ~/.claude/skills' if r.returncode == 0 else '  ! remotion install failed')
    log('remotion: free for individuals and companies of up to 3 people; 4+ need a paid Remotion licence.')


def sync_memory(dry, uninstall):
    old = ''
    if os.path.exists(USER_MEMORY):
        with open(USER_MEMORY, encoding='utf-8') as fh:
            old = fh.read()
    if BEGIN in old and END in old:
        a, b = old.index(BEGIN), old.index(END) + len(END)
        rest = (old[:a] + old[b:]).strip('\n')
    else:
        rest = old.strip('\n')
    new = rest + ('\n' if rest else '') if uninstall else (rest + '\n\n' if rest else '') + block_text()
    if new == old:
        log('memory: ~/.claude/CLAUDE.md already up to date')
        return
    log(f"memory: {'remove' if uninstall else 'write'} T1 block in {USER_MEMORY}")
    if not dry:
        os.makedirs(HOME_CLAUDE, exist_ok=True)
        if old:
            shutil.copyfile(USER_MEMORY, USER_MEMORY + '.bak')
        with open(USER_MEMORY, 'w', encoding='utf-8') as fh:
            fh.write(new)


def run(cmd, dry):
    log('  $ ' + ' '.join(cmd))
    if dry:
        return True
    r = subprocess.run(cmd, text=True, capture_output=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        log('    ' + out.splitlines()[-1])
    return r.returncode == 0


def claude_cli():
    exe = shutil.which('claude')
    if not exe:
        log('  ! the `claude` command is not on PATH. Install Claude Code CLI, or add plugins inside Claude Code with /plugin.')
    return exe


def sync_plugins(dry):
    exe = claude_cli()
    if not exe and not dry:
        return
    exe = exe or 'claude'
    with open(os.path.join(T1, '.claude', 'settings.json'), encoding='utf-8') as fh:
        settings = json.load(fh)
    enabled = [k for k, v in settings.get('enabledPlugins', {}).items() if v]
    used = {k.split('@')[1] for k in enabled}
    for name, m in settings.get('extraKnownMarketplaces', {}).items():
        src = m.get('source', {})
        if name not in used:
            continue  # registered for later, nothing enabled from it
        target = src.get('repo') or src.get('url') or src.get('path')
        if target:
            run([exe, 'plugin', 'marketplace', 'add', target, '--scope', 'user'], dry)
    ok = 0
    for p in enabled:
        ok += run([exe, 'plugin', 'install', p, '--scope', 'user'], dry)
    if dry:
        log(f'plugins: would install {len(enabled)} at user scope')
    else:
        log(f'plugins: {ok}/{len(enabled)} installed at user scope (restart Claude Code to load them)')


def sync_mcp(dry):
    exe = claude_cli()
    if not exe and not dry:
        return
    exe = exe or 'claude'
    with open(os.path.join(T1, '.mcp.json'), encoding='utf-8') as fh:
        servers = json.load(fh).get('mcpServers', {})
    for name, cfg in servers.items():
        cfg = dict(cfg)
        if WINDOWS and cfg.get('command') == 'npx':
            # Claude Code docs: on native Windows, npx servers need the cmd /c wrapper
            cfg = {**cfg, 'command': 'cmd', 'args': ['/c', 'npx'] + cfg.get('args', [])}
        run([exe, 'mcp', 'add-json', '--scope', 'user', name, json.dumps(cfg)], dry)
    log('mcp: needs uv (uvx) and Node.js (npx) installed; blender needs the Blender add-on running; '
        'fivem reads FIVEM_RCON_PASSWORD from your environment. Ask before using them (CLAUDE.md).')


def hook_entry():
    # Exec form (command + args, no shell): works the same under Git Bash, PowerShell and sh,
    # and Windows paths need no escaping. On Windows `command` must be a real .exe (python.exe).
    return {'type': 'command', 'command': sys.executable,
            'args': [os.path.join(T1, 'scripts', 'install_local.py'), '--update'], 'timeout': 60}


def is_t1_hook(h):
    return 'install_local.py' in ' '.join([h.get('command', '')] + list(h.get('args', []))) and \
        '--update' in ' '.join([h.get('command', '')] + list(h.get('args', [])))


def sync_auto_update(dry, uninstall):
    """Add (or remove) a user-level SessionStart hook that pulls T1 and re-links skills."""
    settings = {}
    if os.path.exists(USER_SETTINGS):
        try:
            with open(USER_SETTINGS, encoding='utf-8') as fh:
                settings = json.load(fh)
        except (OSError, ValueError):
            log(f'  ! {USER_SETTINGS} is not valid JSON; auto-update not changed')
            return
    hooks = settings.setdefault('hooks', {})
    groups = hooks.get('SessionStart', [])
    kept = [g for g in groups if not any(is_t1_hook(h) for h in g.get('hooks', []))]
    if not uninstall:
        kept.append({'matcher': 'startup', 'hooks': [hook_entry()]})
    if kept == groups:
        log('auto-update: already set' if not uninstall else 'auto-update: not set')
        return
    if kept:
        hooks['SessionStart'] = kept
    else:
        hooks.pop('SessionStart', None)
        if not hooks:
            settings.pop('hooks', None)
    log(f"auto-update: {'remove' if uninstall else 'add'} SessionStart hook in {USER_SETTINGS}")
    if not dry:
        os.makedirs(HOME_CLAUDE, exist_ok=True)
        if os.path.exists(USER_SETTINGS):
            shutil.copyfile(USER_SETTINGS, USER_SETTINGS + '.bak')
        with open(USER_SETTINGS, 'w', encoding='utf-8') as fh:
            json.dump(settings, fh, indent=2, ensure_ascii=False)
            fh.write('\n')


def enabled_plugins():
    try:
        with open(os.path.join(T1, '.claude', 'settings.json'), encoding='utf-8') as fh:
            return {k for k, v in json.load(fh).get('enabledPlugins', {}).items() if v}
    except (OSError, ValueError):
        return set()


def update():
    """Run by the SessionStart hook: pull T1 quietly and re-link. Never fails the session."""
    QUIET.append('')
    try:
        def git(*a):
            return subprocess.run(['git', '-C', T1] + list(a), capture_output=True, text=True, timeout=40)
        before = git('rev-parse', 'HEAD').stdout.strip()
        plugins_before = enabled_plugins()
        pull = git('pull', '--ff-only', '-q')
        after = git('rev-parse', 'HEAD').stdout.strip()
        if pull.returncode != 0 or not after or after == before:
            return 0  # offline, local changes, or nothing new: stay silent
        sync_skills(False, False)
        sync_agents(False, False)
        sync_memory(False, False)
        new_plugins = sorted(enabled_plugins() - plugins_before)
        msg = f'T1 auto-updated {before[:7]}..{after[:7]}.'
        changes = [m.strip() for m in QUIET[1:] if m.strip().startswith(('skills:', 'agents:', '+ link', '- remove'))]
        if changes:
            msg += ' ' + '; '.join(changes[:6])
        if new_plugins:
            msg += (f' New plugins enabled in T1: {", ".join(new_plugins)} - tell the user to run '
                    f'`python "{T1}/scripts/install_local.py" --plugins` to install them.')
        print(msg, flush=True)
    except Exception:  # noqa: BLE001 - a hook must never break session start
        pass
    return 0


def main():
    ap = argparse.ArgumentParser(description="Use T1's skills and rules in local Claude Code sessions")
    ap.add_argument('--plugins', action='store_true', help='also install the enabled plugins at user scope')
    ap.add_argument('--mcp', action='store_true', help='also add the .mcp.json servers at user scope')
    ap.add_argument('--remotion', action='store_true', help="also install Remotion's video skills (npx skills add remotion-dev/skills)")
    ap.add_argument('--all', action='store_true', help='skills + rules + plugins + mcp + remotion')
    ap.add_argument('--dry-run', action='store_true', help='show what would change')
    ap.add_argument('--auto-update', action='store_true',
                    help='add a SessionStart hook that pulls T1 and re-links skills whenever Claude Code starts')
    ap.add_argument('--update', action='store_true', help=argparse.SUPPRESS)  # used by the hook
    ap.add_argument('--uninstall', action='store_true', help='remove T1 skill links, the CLAUDE.md block and the hook')
    args = ap.parse_args()
    if args.update:
        return update()
    if args.dry_run:
        log('(dry run - nothing is changed)')
    log(f'T1: {T1}\nuser config: {HOME_CLAUDE}')
    sync_skills(args.dry_run, args.uninstall)
    sync_agents(args.dry_run, args.uninstall)
    sync_memory(args.dry_run, args.uninstall)
    if args.auto_update or args.uninstall:
        sync_auto_update(args.dry_run, args.uninstall)
    if args.uninstall:
        log('plugins/MCP are left installed; remove them with `claude plugin uninstall` / `claude mcp remove -s user`.')
        return
    if args.plugins or args.all:
        sync_plugins(args.dry_run)
    if args.mcp or args.all:
        sync_mcp(args.dry_run)
    if args.remotion or args.all:
        sync_remotion(args.dry_run)
    log('done. Open a new local Claude Code session (CLI or desktop "Local") in any folder.')


if __name__ == '__main__':
    sys.exit(main())
