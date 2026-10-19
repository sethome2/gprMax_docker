"""Record/verify upstream Python sources without editing the source tree."""
import hashlib
import json
import sys
from pathlib import Path

root = Path('/opt/gprMax')
manifest = Path('/opt/gprmax-source-manifest.json')
if sys.argv[1] == 'record':
    files = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob('*') if p.is_file() and p.suffix in {'.py', '.pyx', '.pxd', '.h', '.jinja'}
    }
    manifest.write_text(json.dumps(files, sort_keys=True))
else:
    files = json.loads(manifest.read_text())
    for name, expected in files.items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
    # Verify the installed runtime too, not just the retained source tree.
    import gprMax
    installed = Path(gprMax.__file__).parent
    for name, expected in files.items():
        rel = Path(name)
        if rel.parts[0] == 'gprMax' and rel.suffix == '.py':
            target = installed.joinpath(*rel.parts[1:])
            assert target.is_file(), str(target)
            assert hashlib.sha256(target.read_bytes()).hexdigest() == expected, str(target)
    assert not (installed / 'utilities/byte_size.py').exists(), 'Unexpected capacity patch'
    print(f'Unmodified upstream sources verified: {len(files)} files; runtime={installed}')
