# gprMax Docker

English documentation: [README.md](README.md)

这是 gprMax 官方发行版的 Docker 打包仓库，提供独立的 CPU 和 NVIDIA GPU 镜像。

镜像源码来自官方 `v.4.0.1`，并固定到提交 `3ab1c854348a9220beed6ff6925b166a14cfe2b4`。容器会保留发行版源码树，包括 `examples` 和 `tools`。

## 镜像

发布镜像名：

```bash
ghcr.io/sethome2/gprmax-docker
```

Tags:

- `4.0.1-cpu`
- `4.0.1-gpu`
- `latest-cpu`
- `latest-gpu`

CPU 和 GPU 镜像都使用 Python 3.12。GPU 镜像使用 Ubuntu 24.04 和 CUDA 12.6.3，并使用独立虚拟环境。

对于 CPU 版本，本地构建的镜像可能性能更好，因为 gprMax 会针对宿主机 CPU 进行编译。

## 运行

容器默认执行 `python3 -m gprMax "$@"`，工作目录为 `/work`。如果没有绑定挂载目录，`/work/examples`、`/work/tools` 和 `/work/user_libs` 会在对应资源存在时指向 `/opt/gprMax` 下的发行版资源。

运行发行版源码树中的模型：

```bash
docker run --rm ghcr.io/sethome2/gprmax-docker:4.0.1-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

通过挂载目录运行你自己的模型：

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.1-cpu model.in
```

### 传递 gprMax 参数

镜像名后面的参数会直接传给 gprMax。例如，下面的命令等价于 `python -m gprMax cylinder_Bscan_GSSI_1500.in -n 54`：

```bash
docker run --rm -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.1-cpu cylinder_Bscan_GSSI_1500.in -n 54
```

GPU 运行：

```bash
docker run --rm --gpus all -v "$PWD":/work ghcr.io/sethome2/gprmax-docker:4.0.1-gpu model.in -gpu
```

GPU 镜像要求宿主机上有可用的 NVIDIA 驱动和 NVIDIA Container Toolkit。镜像中包含 CUDA Toolkit 组件，因为 gprMax 会使用 PyCUDA 在运行时编译 CUDA kernel。

通过覆盖 entrypoint 运行辅助模块：

```bash
docker run --rm -v "$PWD":/work --entrypoint python3 ghcr.io/sethome2/gprmax-docker:4.0.1-cpu -m tools.plot_Ascan file.h5
```

## 本地构建

CPU/noGPU 镜像：

```bash
docker build -f Dockerfile.cpu -t gprmax:4.0.1-cpu .
```

GPU 镜像：

```bash
docker build -f Dockerfile.gpu -t gprmax:4.0.1-gpu .
```

覆盖要打包的 gprMax 发行版：

```bash
docker build \
  -f Dockerfile.cpu \
  --build-arg GPRMAX_VERSION=4.0.1 \
  --build-arg GPRMAX_REVISION=3ab1c854348a9220beed6ff6925b166a14cfe2b4 \
  -t gprmax:4.0.1-cpu .
```

## Smoke Tests

CPU：

```bash
docker run --rm gprmax:4.0.1-cpu --help
docker run --rm gprmax:4.0.1-cpu examples/gpr/basic/cylinder_Ascan_2D.in
```

GPU，在宿主机 GPU runtime 正常后运行：

```bash
docker run --rm --gpus all gprmax:4.0.1-gpu --help
docker run --rm --gpus all gprmax:4.0.1-gpu examples/gpr/basic/cylinder_Ascan_2D.in -gpu
```

## 发布 Workflow

GitHub Actions workflow 会在 push 到 `main`、push tag 和手动触发时构建并发布 CPU/GPU 镜像到 GHCR。CPU 镜像会在 CI 中执行 `--help` smoke test。GPU 镜像只构建和推送，因为 GitHub-hosted runner 不提供 NVIDIA GPU。

## 范围

本仓库用于打包官方 gprMax 发行版，不会 fork 或 patch gprMax 源码。专用 MPI 镜像变体留待未来实现。


## 官方源码同步与发布通道

镜像仅封装官方原始源码，不允许覆盖或修改求解器源码。生产升级使用验证通过的不可变 digest。

| 通道 | CPU tag | GPU tag | 官方来源 |
| --- | --- | --- | --- |
| v4 正式版 | `v4-cpu` | `v4-gpu` | 最新 v4 正式 release，目前 4.0.1 |
| v3 正式版 | `v3-cpu` | `v3-gpu` | 最新 v3 正式 release，目前 3.1.7 |
| 开发版 | `devel-cpu` | `devel-gpu` | 官方 `master`，不是已删除的 `devel` 分支 |

同时发布精确版本 tag，`latest-cpu/gpu` 指向 v4；历史 tag 保留。v3 镜像供独立使用，不接入 Workbench 的 v4 结果链路。

Actions 在 main 代码推送、手动触发及每天北京时间 11:17 检查更新；定时任务仅重建源码或封装提交变化的通道。
每次先解析确切官方 commit，再构建 CPU/GPU 候选镜像。完整矩阵全部成功后才更新正式 tag。
所有候选检查版本、帮助命令及源码/安装目录 SHA-256；CPU 还执行两轮最小仿真，验证 v3 `.out` / v4 `.h5` 的有限且非零接收器数据。
GitHub 托管 runner 不提供 NVIDIA GPU，因此真实 GPU 求解在 worker 上另行验收。

`upstream-channels`、`release-manifest` 构建产物记录上游引用、源码 commit、封装 commit 和镜像 digest。
构建通过独立编译器包装脚本移除 CI 主机专用指令集选项，不修改上游 setup.py。
源码校验清单位于 `/opt/gprmax-source-manifest.json`，可执行：

```bash
docker run --rm --entrypoint python3 IMAGE /usr/local/libexec/source_manifest.py verify
```

发布镜像不会自动重启 worker；生产升级需单独取消/排空任务、拉取镜像并固定 digest。
容量补丁镜像的退出情况见 Worker 仓库部署记录。

注意：官方 `v.3.1.7` tag 的 `_version.py` 仍声明 `3.1.6`。本仓库保留该上游差异，
镜像 tag 使用发布版本 3.1.7，`io.gprmax.runtime-version`、`GPRMAX_RUNTIME_VERSION`
及发布清单记录实际运行版本 3.1.6；不修改源码版本文件。
