# gprMax Docker

简体中文文档: [README_zh.md](README_zh.md)

Docker packaging for the official gprMax release, with separate CPU and NVIDIA GPU images.

The default release source is the official `v.3.1.7` GitHub tag. That tag currently reports `v3.1.6` in the gprMax runtime banner/egg metadata, so the Docker image tag tracks the upstream release tag rather than the internal banner string. The container keeps the release source tree, including `user_models` and `tools`.

## Images

Published image name:

```bash
ghcr.io/sethome2/gprmax-docker
```

Tags:

- `3.1.7-cpu`
- `3.1.7-gpu`
- `latest-cpu`
- `latest-gpu`

## Run

The containers default to `python3 -m gprMax "$@"`, with `/work` as the working directory. Without a bind mount, `/work/user_models`, `/work/tools`, and `/work/user_libs` point to the packaged release resources under `/opt/gprMax`.

Run a model from the release source tree:

```bash
docker run --rm ghcr.io/sethome2/gprmax-docker:3.1.7-cpu user_models/cylinder_Ascan_2D.in
```

Run your own models by mounting a directory:

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:3.1.7-cpu model.in
```

GPU run:

```bash
docker run --rm --gpus all -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:3.1.7-gpu model.in -gpu
```

The GPU image requires a working NVIDIA driver and NVIDIA Container Toolkit on the host. The image includes CUDA Toolkit components because gprMax uses PyCUDA to compile CUDA kernels at runtime.

Run helper modules by overriding the entrypoint:

```bash
docker run --rm -v "$PWD":/work --entrypoint python3 ghcr.io/sethome2/gprmax-docker:3.1.7-cpu -m tools.plot_Ascan file.out
```

## Build Locally

CPU/noGPU image:

```bash
docker build -f Dockerfile.cpu -t gprmax:3.1.7-cpu .
```

GPU image:

```bash
docker build -f Dockerfile.gpu -t gprmax:3.1.7-gpu .
```

Override the packaged gprMax release:

```bash
docker build \
  -f Dockerfile.cpu \
  --build-arg GPRMAX_VERSION=3.1.7 \
  --build-arg GPRMAX_TAG=v.3.1.7 \
  -t gprmax:3.1.7-cpu .
```

## Smoke Tests

CPU:

```bash
docker run --rm gprmax:3.1.7-cpu --help
docker run --rm gprmax:3.1.7-cpu user_models/cylinder_Ascan_2D.in
```

GPU, after host GPU runtime is working:

```bash
docker run --rm --gpus all gprmax:3.1.7-gpu --help
docker run --rm --gpus all gprmax:3.1.7-gpu user_models/cylinder_Ascan_2D.in -gpu
```

## Release Workflow

The GitHub Actions workflow builds and publishes CPU/GPU images to GHCR on pushes to `main`, tags, and manual dispatches. CPU gets a `--help` smoke test in CI. GPU is build/push only because GitHub-hosted runners do not provide NVIDIA GPUs.

## Scope

This repository packages official gprMax releases. It does not fork or patch gprMax source code. MPI/OpenMPI support is intentionally left for a future image variant.
