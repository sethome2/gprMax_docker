# gprMax Docker

简体中文文档: [README_zh.md](README_zh.md)

Docker packaging for official gprMax releases, with separate CPU and NVIDIA GPU images.

The packaged source is the official `v.4.0.0` release, pinned to commit `116685ebb8d6f68015ea7cda993f1bd7c21f96f1`. The container keeps the release source tree, including `examples` and `tools`.

## Images

Published image name:

```bash
ghcr.io/sethome2/gprmax-docker
```

Tags:

- `4.0.0-cpu`
- `4.0.0-gpu`
- `latest-cpu`
- `latest-gpu`

Both images use Python 3.12. The GPU image uses CUDA 12.6.3 on Ubuntu 24.04 with Python in an isolated virtual environment.

For the CPU version, a locally built image may perform better because gprMax is compiled for your host CPU.

## Run

The containers default to `python3 -m gprMax "$@"`, with `/work` as the working directory. Without a bind mount, `/work/examples`, `/work/tools`, and `/work/user_libs` point to packaged resources under `/opt/gprMax` when present.

Run a model from the release source tree:

```bash
docker run --rm ghcr.io/sethome2/gprmax-docker:4.0.0-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

Run your own models by mounting a directory:

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.0-cpu model.in
```

### Passing gprMax arguments

Arguments after the image name are passed directly to gprMax. For example, this is equivalent to `python -m gprMax cylinder_Bscan_GSSI_1500.in -n 54`:

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.0-cpu cylinder_Bscan_GSSI_1500.in -n 54
```

GPU run:

```bash
docker run --rm --gpus all -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.0-gpu model.in -gpu
```

The GPU image requires a working NVIDIA driver and NVIDIA Container Toolkit on the host. The image includes CUDA Toolkit components because gprMax uses PyCUDA to compile CUDA kernels at runtime.

Run helper modules by overriding the entrypoint:

```bash
docker run --rm -v "$PWD":/work --entrypoint python3 ghcr.io/sethome2/gprmax-docker:4.0.0-cpu -m tools.plot_Ascan file.h5
```

## Build Locally

CPU/noGPU image:

```bash
docker build -f Dockerfile.cpu -t gprmax:4.0.0-cpu .
```

GPU image:

```bash
docker build -f Dockerfile.gpu -t gprmax:4.0.0-gpu .
```

Override the packaged gprMax release:

```bash
docker build \
  -f Dockerfile.cpu \
  --build-arg GPRMAX_VERSION=4.0.0 \
  --build-arg GPRMAX_REVISION=116685ebb8d6f68015ea7cda993f1bd7c21f96f1 \
  -t gprmax:4.0.0-cpu .
```

## Smoke Tests

CPU:

```bash
docker run --rm gprmax:4.0.0-cpu --help
docker run --rm gprmax:4.0.0-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

GPU, after host GPU runtime is working:

```bash
docker run --rm --gpus all gprmax:4.0.0-gpu --help
docker run --rm --gpus all gprmax:4.0.0-gpu examples/gpr/basic/cylinder_Ascan_2D.in -gpu
```

## Release Workflow

The GitHub Actions workflow builds and publishes CPU/GPU images to GHCR on pushes to `main`, tags, and manual dispatches. CPU gets a `--help` smoke test in CI. GPU is build/push only because GitHub-hosted runners do not provide NVIDIA GPUs.

## Scope

This repository packages an official gprMax release without patching its source code. A dedicated MPI image variant is intentionally left for the future.
