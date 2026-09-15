# gprMax Docker

English documentation: [README.md](README.md)

这是 gprMax 官方发行版的 Docker 打包仓库，提供独立的 CPU 和 NVIDIA GPU 镜像。

镜像源码来自官方 `v.4.0.0`，并固定到提交 `116685ebb8d6f68015ea7cda993f1bd7c21f96f1`。容器会保留发行版源码树，包括 `examples` 和 `tools`。

## 镜像

发布镜像名：

```bash
ghcr.io/sethome2/gprmax-docker
```

Tags:

- `4.0.0-cpu`
- `4.0.0-gpu`
- `latest-cpu`
- `latest-gpu`

CPU 和 GPU 镜像都使用 Python 3.12。GPU 镜像使用 Ubuntu 24.04 和 CUDA 12.6.3，并使用独立虚拟环境。

对于 CPU 版本，本地构建的镜像可能性能更好，因为 gprMax 会针对宿主机 CPU 进行编译。

## 运行

容器默认执行 `python3 -m gprMax "$@"`，工作目录为 `/work`。如果没有绑定挂载目录，`/work/examples`、`/work/tools` 和 `/work/user_libs` 会在对应资源存在时指向 `/opt/gprMax` 下的发行版资源。

运行发行版源码树中的模型：

```bash
docker run --rm ghcr.io/sethome2/gprmax-docker:4.0.0-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

通过挂载目录运行你自己的模型：

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.0-cpu model.in
```

### 传递 gprMax 参数

镜像名后面的参数会直接传给 gprMax。例如，下面的命令等价于 `python -m gprMax cylinder_Bscan_GSSI_1500.in -n 54`：

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.0-cpu cylinder_Bscan_GSSI_1500.in -n 54
```

GPU 运行：

```bash
docker run --rm --gpus all -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.0-gpu model.in -gpu
```

GPU 镜像要求宿主机上有可用的 NVIDIA 驱动和 NVIDIA Container Toolkit。镜像中包含 CUDA Toolkit 组件，因为 gprMax 会使用 PyCUDA 在运行时编译 CUDA kernel。

通过覆盖 entrypoint 运行辅助模块：

```bash
docker run --rm -v "$PWD":/work --entrypoint python3 ghcr.io/sethome2/gprmax-docker:4.0.0-cpu -m tools.plot_Ascan file.h5
```

## 本地构建

CPU/noGPU 镜像：

```bash
docker build -f Dockerfile.cpu -t gprmax:4.0.0-cpu .
```

GPU 镜像：

```bash
docker build -f Dockerfile.gpu -t gprmax:4.0.0-gpu .
```

覆盖要打包的 gprMax 发行版：

```bash
docker build \
  -f Dockerfile.cpu \
  --build-arg GPRMAX_VERSION=4.0.0 \
  --build-arg GPRMAX_REVISION=116685ebb8d6f68015ea7cda993f1bd7c21f96f1 \
  -t gprmax:4.0.0-cpu .
```

## Smoke Tests

CPU：

```bash
docker run --rm gprmax:4.0.0-cpu --help
docker run --rm gprmax:4.0.0-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

GPU，在宿主机 GPU runtime 正常后运行：

```bash
docker run --rm --gpus all gprmax:4.0.0-gpu --help
docker run --rm --gpus all gprmax:4.0.0-gpu examples/gpr/basic/cylinder_Ascan_2D.in -gpu
```

## 发布 Workflow

GitHub Actions workflow 会在 push 到 `main`、push tag 和手动触发时构建并发布 CPU/GPU 镜像到 GHCR。CPU 镜像会在 CI 中执行 `--help` smoke test。GPU 镜像只构建和推送，因为 GitHub-hosted runner 不提供 NVIDIA GPU。

## 范围

本仓库用于打包官方 gprMax 发行版，不会 fork 或 patch gprMax 源码。专用 MPI 镜像变体留待未来实现。
