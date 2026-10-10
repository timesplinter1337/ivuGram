'''
Helpers for .github/workflows/win-local.yml, run with plain python so that
the PowerShell execution policy of the local machine does not matter.

Usage: win_local.py stamp | summary
'''
import datetime, hashlib, os, pathlib, re, sys

def append(path, text):
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(text)

def stamp():
    src = pathlib.Path(os.environ['SRC'])
    tbuild = pathlib.Path(os.environ['TBUILD'])
    files = sorted(p for p in (src / 'Telegram' / 'build' / 'prepare').rglob('*') if p.is_file())
    files.append(src / 'Telegram' / 'build' / 'qt_version.py')

    doc = (src / 'docs' / 'building-win.md').read_text(encoding='utf-8')
    match = re.search(r'\*\*([\d.]+)\*\*\s+SDK version', doc)
    if not match:
        sys.exit('SDK version not found in docs/building-win.md')
    sdk = match.group(1)

    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(src).as_posix().encode('utf-8'))
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    digest.update(sdk.encode('utf-8'))
    value = digest.hexdigest()

    stampFile = tbuild / '.ivugram-libs-stamp'
    old = stampFile.read_text(encoding='utf-8').strip() if stampFile.exists() else ''
    changed = 'false' if old == value else 'true'
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()

    append(os.environ['GITHUB_ENV'],
        'SDK=' + sdk + '\n'
        + 'LIBS_STAMP=' + value + '\n'
        + 'LIBS_CHANGED=' + changed + '\n'
        + 'JOB_START=' + start + '\n')
    print('SDK ' + sdk + ', libraries changed: ' + changed)

def summary():
    target = os.environ.get('GITHUB_STEP_SUMMARY')
    if not target:
        return
    lines = ['### Windows x64 Debug (local runner)', '']
    lines.append('* Commit: `' + os.environ.get('GITHUB_SHA', '')[:10] + '`')
    start = os.environ.get('JOB_START')
    if start:
        span = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(start)
        seconds = int(span.total_seconds())
        lines.append('* Time since sources were synced: %d min %d s' % (seconds // 60, seconds % 60))
    lines.append('* Libraries rebuilt: ' + ('yes' if os.environ.get('LIBS_CHANGED') == 'true' else 'no'))
    src = os.environ.get('SRC')
    exe = pathlib.Path(src) / 'out' / 'Debug' / 'Telegram.exe' if src else None
    if exe and exe.exists():
        info = exe.stat()
        built = datetime.datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        lines.append('* Telegram.exe: %d MB, built %s' % (info.st_size // (1024 * 1024), built))
    append(target, '\n'.join(lines) + '\n')

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else ''
    if command == 'stamp':
        stamp()
    elif command == 'summary':
        summary()
    else:
        sys.exit('Usage: win_local.py stamp | summary')
