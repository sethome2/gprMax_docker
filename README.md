# gprMax Docker

简体中文文档: [README_zh.md](README_zh.md)

Docker packaging for official gprMax releases, with separate CPU and NVIDIA GPU images.

Images contain unmodified official source archives, resolved to exact upstream commits. Three channels track the newest v4 release, newest v3 release, and the official `master` development branch. The source tree and its SHA-256 manifest remain in the container.

## Images

Published image name:

```bash
ghcr.io/sethome2/gprmax-docker
```

Maintained tags (each has CPU and GPU variants):

| Channel | CPU | GPU | Official source |
| --- | --- | --- | --- |
| v4 stable | `v4-cpu` | `v4-gpu` | Latest non-prerelease v4 release (currently 4.0.1) |
| v3 stable | `v3-cpu` | `v3-gpu` | Latest non-prerelease v3 release (currently 3.1.7) |
| development | `devel-cpu` | `devel-gpu` | `gprMax/gprMax` `master` |

Exact release tags such as `4.0.1-cpu` / `4.0.1-gpu` are also published.
`latest-cpu` / `latest-gpu` alias v4. Historical tags are retained.
Production deployments must pull and pin the verified `@sha256:...` digest;
channel tags do not automatically upgrade workers. v3 images are standalone and
are not supported by the Workbench v4 result pipeline.

The official `v.3.1.7` source declares runtime version `3.1.6`. This upstream
discrepancy is preserved: image/release tags identify 3.1.7, while
`io.gprmax.runtime-version`, `GPRMAX_RUNTIME_VERSION` and the release manifest
record 3.1.6. Source version files are never rewritten.

Both images use Python 3.12. The GPU image uses CUDA 12.6.3 on Ubuntu 24.04 with Python in an isolated virtual environment.

CPU extensions use a portable x86-64 target so the same image can run across worker hosts.

## Run

The containers default to `python3 -m gprMax "$@"`, with `/work` as the working directory. Without a bind mount, `/work/examples`, `/work/tools`, and `/work/user_libs` point to packaged resources under `/opt/gprMax` when present.

Run a model from the release source tree:

```bash
docker run --rm ghcr.io/sethome2/gprmax-docker:4.0.1-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

Run your own models by mounting a directory:

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.1-cpu model.in
```

### Passing gprMax arguments

Arguments after the image name are passed directly to gprMax. For example, this is equivalent to `python -m gprMax cylinder_Bscan_GSSI_1500.in -n 54`:

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.1-cpu cylinder_Bscan_GSSI_1500.in -n 54
```

GPU run:

```bash
docker run --rm --gpus all -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.1-gpu model.in -gpu
```

The GPU image requires a working NVIDIA driver and NVIDIA Container Toolkit on the host. The image includes CUDA Toolkit components because gprMax uses PyCUDA to compile CUDA kernels at runtime.

Run helper modules by overriding the entrypoint:

```bash
docker run --rm -v "$PWD":/work --entrypoint python3 ghcr.io/sethome2/gprmax-docker:4.0.1-cpu -m tools.plot_Ascan file.h5
```

## Build Locally

CPU/noGPU image:

```bash
docker build -f Dockerfile.cpu -t gprmax:4.0.1-cpu .
```

GPU image:

```bash
docker build -f Dockerfile.gpu -t gprmax:4.0.1-gpu .
```

Override the packaged gprMax release:

```bash
docker build \
  -f Dockerfile.cpu \
  --build-arg GPRMAX_VERSION=4.0.1 \
  --build-arg GPRMAX_REVISION=3ab1c854348a9220beed6ff6925b166a14cfe2b4 \
  -t gprmax:4.0.1-cpu .
```

## Smoke Tests

CPU:

```bash
docker run --rm gprmax:4.0.1-cpu --help
docker run --rm gprmax:4.0.1-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

GPU, after host GPU runtime is working:

```bash
docker run --rm --gpus all gprmax:4.0.1-gpu --help
docker run --rm --gpus all gprmax:4.0.1-gpu examples/gpr/basic/cylinder_Ascan_2D.in -gpu
```

## Release Workflow

The workflow runs on code pushes to `main`, manual dispatch, and daily at 03:17 UTC
(11:17 China time). It resolves release tags (including annotated tags) and `master`
to exact commits before building. Scheduled runs skip channels whose source and
packaging commits already have published candidates.

All six initial candidates must pass source/runtime integrity checks, version checks
and `--help`. CPU candidates additionally run two traces and validate HDF5 output
(v3 `.out`, v4 `.h5`, finite nonzero receiver fields). Only after the complete build
matrix succeeds are channel/version aliases promoted. GPU execution must additionally
be verified on NVIDIA worker hardware; CI does not claim GPU simulation coverage.

The `upstream-channels` and `release-manifest` Actions artifacts record official refs,
commits, packaging commit and published digests. Candidate tags start with `build-`.
Images use a compiler wrapper to replace host-specific `-march=native` flags with a
portable x86-64 target without editing upstream setup scripts. The integrity manifest
is `/opt/gprmax-source-manifest.json`; verify it with:

```bash
docker run --rm --entrypoint python3 IMAGE /usr/local/libexec/source_manifest.py verify
```

Do not add source patches or copy local solver modules over installed gprMax.
For the removal of the former capacity patch, see the Worker deployment records.

## Scope

This repository packages an official gprMax release without patching its source code. A dedicated MPI image variant is intentionally left for the future.
