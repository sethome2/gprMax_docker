# gprMax Docker

English documentation: [README.md](README.md)

这是官方 gprMax 发行版的 Docker 打包仓库，提供独立的 CPU 和 NVIDIA GPU 镜像。

默认发行版源码来自官方 `v.3.1.7` GitHub tag。该 tag 目前在 gprMax 运行时 banner 和 egg metadata 中显示为 `v3.1.6`，因此 Docker 镜像 tag 跟随上游 release tag，而不是内部 banner 字符串。容器会保留发行版源码树，包括 `user_models` 和 `tools`。

## 镜像

发布镜像名：

```bash
ghcr.io/sethome2/gprmax-docker
```

Tags:

- `3.1.7-cpu`
- `3.1.7-gpu`
- `latest-cpu`
- `latest-gpu`

对于 CPU 版本，本地构建的镜像可能性能更好，因为 gprMax 会针对宿主机 CPU 进行编译。

## 运行

容器默认执行 `python3 -m gprMax "$@"`，工作目录为 `/work`。如果没有绑定挂载目录，`/work/user_models`、`/work/tools` 和 `/work/user_libs` 会指向 `/opt/gprMax` 下打包好的发行版资源。

运行发行版源码树中的模型：

```bash
docker run --rm ghcr.io/sethome2/gprmax-docker:3.1.7-cpu user_models/cylinder_Ascan_2D.in
```

通过挂载目录运行你自己的模型：

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:3.1.7-cpu model.in
```

GPU 运行：

```bash
docker run --rm --gpus all -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:3.1.7-gpu model.in -gpu
```

GPU 镜像要求宿主机上有可用的 NVIDIA 驱动和 NVIDIA Container Toolkit。镜像中包含 CUDA Toolkit 组件，因为 gprMax 会使用 PyCUDA 在运行时编译 CUDA kernel。

通过覆盖 entrypoint 运行辅助模块：

```bash
docker run --rm -v "$PWD":/work --entrypoint python3 ghcr.io/sethome2/gprmax-docker:3.1.7-cpu -m tools.plot_Ascan file.out
```

## 本地构建

CPU/noGPU 镜像：

```bash
docker build -f Dockerfile.cpu -t gprmax:3.1.7-cpu .
```

GPU 镜像：

```bash
docker build -f Dockerfile.gpu -t gprmax:3.1.7-gpu .
```

覆盖要打包的 gprMax 发行版：

```bash
docker build \
  -f Dockerfile.cpu \
  --build-arg GPRMAX_VERSION=3.1.7 \
  --build-arg GPRMAX_TAG=v.3.1.7 \
  -t gprmax:3.1.7-cpu .
```

## Smoke Tests

CPU：

```bash
docker run --rm gprmax:3.1.7-cpu --help
docker run --rm gprmax:3.1.7-cpu user_models/cylinder_Ascan_2D.in
```

GPU，在宿主机 GPU runtime 正常后运行：

```bash
docker run --rm --gpus all gprmax:3.1.7-gpu --help
docker run --rm --gpus all gprmax:3.1.7-gpu user_models/cylinder_Ascan_2D.in -gpu
```

## 发布 Workflow

GitHub Actions workflow 会在 push 到 `main`、push tag 和手动触发时构建并发布 CPU/GPU 镜像到 GHCR。CPU 镜像会在 CI 中执行 `--help` smoke test。GPU 镜像只构建和推送，因为 GitHub-hosted runner 不提供 NVIDIA GPU。

## 范围

本仓库用于打包官方 gprMax 发行版。它不会 fork 或 patch gprMax 源码。MPI/OpenMPI 支持有意留给未来的镜像变体。
