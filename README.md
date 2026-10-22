# HSV Sphere

使用 Plotly 展示图像在 HSV、HSL 和 CIELCH 色彩空间中的三维颜色分布。

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
