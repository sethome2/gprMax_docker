#!/bin/sh
set -eu
python3 /usr/local/libexec/source_manifest.py record
if [ "${GPRMAX_VERSION%%.*}" = 3 ]; then
    # The unmodified v3 setup.py requires dependencies before building.
    python3 -m pip install colorama cython h5py jupyter matplotlib numpy psutil scipy terminaltables tqdm
    if [ "$GPRMAX_VARIANT" = gpu ]; then python3 -m pip install pycuda; fi
    python3 setup.py build
    python3 setup.py install
else
    if [ "$GPRMAX_VARIANT" = gpu ]; then
        python3 -m pip install '.[cuda]'
    else
        python3 -m pip install .
    fi
fi
cd /tmp
python3 -c 'import gprMax, os; assert gprMax.__version__ == os.environ["GPRMAX_RUNTIME_VERSION"], gprMax.__version__'
python3 /usr/local/libexec/source_manifest.py verify
