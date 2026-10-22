# Image Color Distribution

使用 Plotly 展示图像在 HSV、HSL 和 CIELCH 色彩空间中的三维颜色分布。

## 网页版

访问 **[在线可视化](https://recynie.github.io/image-color-distribution/)**，选择图片或试用示例，选择色彩空间和点云精度，点击“生成可视化”。支持 JPEG、PNG、WebP（最大 20 MB，最多 2,500 万像素）。拖动旋转、滚轮缩放，可通过图表工具栏保存 PNG。

图片仅在浏览器本地处理，不发送服务器。页面通过 Pyodide 在 Web Worker 中运行 Python，`color_distribution.py` 直接复用 `HSV-ds.py`、`HSL-ds.py`、`CIELCH-ds.py` 的颜色计算、坐标映射和参考线，没有另写 JavaScript 颜色转换。`HSV.py` 仍作为原始 OpenCV 桌面示例保留；网页 HSV 使用球形映射版本 `HSV-ds.py`。

首次生成需要从 jsDelivr / PyPI 下载 Python 运行时及依赖，可能需要数十秒，具体取决于网络。Plotly.js 从 Plotly CDN 加载。需要支持 WebAssembly、Web Workers、WebGL 的现代浏览器和可访问这些服务的网络。桌面依赖由 `uv.lock` 锁定；浏览器二进制依赖由固定的 Pyodide 0.27.7 发行版提供，Python Plotly 固定为 6.3.0。

网页在计算前将图片最长边限制到 1,024 像素，自动校正 EXIF 方向并将透明区域合成到白色背景。HSV/HSL 按原脚本缩放到方形采样网格；CIELCH 沿用展平后的间隔采样。点云精度控制计算量，图片预处理可能使网页与原尺寸桌面输出略有差异。

### 本地预览网页

```bash
uv run python -m http.server 8000 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8000>。请通过 HTTP 访问，直接打开 `index.html` 无法正常加载 Worker 和 Python 文件。

### GitHub Pages 部署

`.github/workflows/pages.yml` 会在推送 `main` 时发布静态网页。仓库 **Settings → Pages → Source** 应选择 **GitHub Actions**。发布内容仅包含网页、共享 Python 入口、三个原始脚本和示例图片，无需 Node.js 构建或 Python 后端。

### 测试

```bash
uv run python -m unittest discover -s tests -v
```

测试验证三种色彩空间的图表生成、采样上限及共享入口不会弹出浏览器。

## 环境与依赖

项目使用 **uv** 管理 Python 3.13 和依赖，无需 Conda。
请先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)。

在项目根目录执行：

```bash
# 如果当前激活了 Conda 环境，先执行 conda deactivate
uv sync --locked
```

uv 会自动获取所需的 Python，并在项目目录创建 `.venv`。
`pyproject.toml` 声明直接依赖，`uv.lock` 固定完整依赖版本；两者均应提交到版本控制。
原有 Conda 环境可以保留，运行本项目时无需激活它。

## 运行

在项目根目录运行，以便脚本读取 `test-images/` 中的示例图片：

```bash
uv run HSV.py
uv run HSV-ds.py
uv run HSL-ds.py
uv run CIELCH-ds.py
```

脚本会通过 Plotly 显示交互式图形，通常在浏览器中打开。
可以在各脚本中修改图片路径及可视化参数。
请使用 `uv run` 启动脚本，确保使用项目的 Python 和依赖。

## 维护依赖

```bash
# 添加或移除依赖，同时更新 pyproject.toml、uv.lock 和 .venv
uv add <包名>
uv remove <包名>

# 在 pyproject.toml 约束范围内更新锁定版本并同步环境
uv lock --upgrade
uv sync --locked
```
