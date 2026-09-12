#!/usr/bin/env sh
set -e

exec "${GPRMAX_PYTHON:-python3}" -m gprMax "$@"
