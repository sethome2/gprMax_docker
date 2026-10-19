"""Run inside a candidate container: tiny two-trace CPU/GPU simulation."""
import os
import subprocess
import sys
from pathlib import Path

import h5py
import numpy as np

subprocess.run([sys.executable, '/usr/local/libexec/source_manifest.py', 'verify'], check=True)
subprocess.run([sys.executable, '-m', 'gprMax', '--help'], check=True)
Path('smoke.in').write_text('''#title: unmodified upstream image smoke
#domain: 0.06 0.06 0.06
#dx_dy_dz: 0.002 0.002 0.002
#time_window: 1e-10
#waveform: ricker 1 1e9 pulse
#hertzian_dipole: z 0.03 0.03 0.03 pulse
#rx: 0.04 0.03 0.03
''')
command = [sys.executable, '-m', 'gprMax', 'smoke.in', '-n', '2']
if '--gpu' in sys.argv:
    command.append('-gpu')
subprocess.run(command, check=True)
version = os.environ['GPRMAX_VERSION']
extension = '.out' if version.startswith('3.') else '.h5'
files = sorted(Path('.').glob('smoke*' + extension))
assert len(files) == 2, files
for path in files:
    with h5py.File(path) as result:
        assert str(result.attrs['gprMax']) == version, dict(result.attrs)
        arrays = []
        result.visititems(lambda name, obj: arrays.append(obj[()]) if isinstance(obj, h5py.Dataset) and name.startswith('rxs/') else None)
        assert arrays and all(np.isfinite(array).all() for array in arrays)
        assert any(np.any(array != 0) for array in arrays)
print(f'SMOKE_OK {version} {extension} traces={len(files)} gpu={"--gpu" in sys.argv}')
