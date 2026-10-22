"use strict";

// Pinned runtime: Python and binary scientific wheels are supplied by Pyodide.
const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/';
let runtimePromise;

function progress(message) {
  self.postMessage({ type: 'status', message });
}

async function initialize() {
  importScripts(`${PYODIDE_URL}pyodide.js`);
  progress('正在加载浏览器中的 Python…');
  const pyodide = await loadPyodide({ indexURL: PYODIDE_URL });
  progress('正在加载 NumPy、Pillow、scikit-image 与 Matplotlib，首次下载较大…');
  await pyodide.loadPackage(['numpy', 'pillow', 'scikit-image', 'matplotlib', 'micropip']);
  progress('正在加载 Python Plotly 和项目原有脚本…');
  await pyodide.runPythonAsync(`
import micropip
await micropip.install('plotly==6.3.0')
`);
  pyodide.FS.mkdir('/app');
  await Promise.all(['color_distribution.py', 'HSV-ds.py', 'HSL-ds.py', 'CIELCH-ds.py'].map(async (name) => {
    const response = await fetch(new URL(name, self.location.href));
    if (!response.ok) throw new Error(`无法读取 ${name}: HTTP ${response.status}`);
    pyodide.FS.writeFile(`/app/${name}`, await response.text());
  }));
  await pyodide.runPythonAsync(`
import sys
sys.path.insert(0, '/app')
import io
import warnings
import numpy as np
from PIL import Image, ImageOps
from color_distribution import build_figure
# Reject oversized decoded images before allocating scientific arrays.
Image.MAX_IMAGE_PIXELS = 25_000_000
warnings.simplefilter('error', Image.DecompressionBombWarning)

def render_image(data, space, side):
    with Image.open(io.BytesIO(bytes(data))) as source:
        image = ImageOps.exif_transpose(source)
        image.thumbnail((1024, 1024))
        # Composite transparency onto white, including palette PNG images.
        rgba = image.convert('RGBA')
        background = Image.new('RGBA', rgba.size, 'white')
        rgb = np.array(Image.alpha_composite(background, rgba).convert('RGB'))
    fig = build_figure(rgb, space, side)
    return fig.to_json(), len(fig.data[0].x)
`);
  return pyodide;
}

self.onmessage = async ({ data }) => {
  let imageBytes;
  let result;
  try {
    runtimePromise ??= initialize().catch((error) => {
      runtimePromise = undefined;
      throw error;
    });
    const pyodide = await runtimePromise;
    progress('正在用原始 Python 脚本计算颜色分布…');
    imageBytes = pyodide.toPy(new Uint8Array(data.buffer));
    const render = pyodide.globals.get('render_image');
    try {
      result = render(imageBytes, data.space, data.side);
      const [figure, points] = result.toJs();
      self.postMessage({ type: 'result', figure, points });
    } finally {
      render.destroy();
    }
  } catch (error) {
    console.error(error);
    let message = error.message.trim().split('\n').at(-1);
    if (message.includes('UnidentifiedImageError')) {
      message = '无法解码图片，请选择有效的 JPEG、PNG 或 WebP 文件';
    } else if (message.includes('DecompressionBomb')) {
      message = '图片像素过多，请缩小到 2,500 万像素以内';
    }
    self.postMessage({ type: 'error', message });
  } finally {
    imageBytes?.destroy();
    result?.destroy();
  }
};
