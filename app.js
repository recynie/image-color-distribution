"use strict";

const fileInput = document.querySelector('#image-file');
const sampleButton = document.querySelector('#sample');
const renderButton = document.querySelector('#render');
const spaceInput = document.querySelector('#space');
const samplesInput = document.querySelector('#samples');
const status = document.querySelector('#status');
const plot = document.querySelector('#plot');
let selectedFile;
let previewURL;
let worker;
let busy = false;
let needsRender = false;

function updateStateLabel() {
  document.querySelector('#state-label').textContent = busy ? '处理中'
    : status.dataset.error === 'true' ? '需重试'
    : needsRender ? '待生成'
    : plot.data ? '已生成' : '待开始';
}

function setStatus(message, error = false) {
  status.textContent = message;
  status.dataset.error = String(error);
  status.parentElement.dataset.error = String(error);
  updateStateLabel();
}

function setBusy(value) {
  busy = value;
  for (const control of [fileInput, sampleButton, spaceInput, samplesInput]) control.disabled = value;
  renderButton.disabled = value || !selectedFile;
  renderButton.textContent = value ? '正在处理…' : '生成可视化';
  plot.setAttribute('aria-busy', String(value));
  updateStateLabel();
}

async function selectFile(file) {
  if (!file) return;
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
    setStatus('请选择 JPEG、PNG 或 WebP 图片。', true);
    return;
  }
  if (file.size > 20 * 1024 * 1024) {
    setStatus('图片超过 20 MB，请先缩小图片。', true);
    return;
  }
  if (previewURL) URL.revokeObjectURL(previewURL);
  selectedFile = file;
  needsRender = true;
  previewURL = URL.createObjectURL(file);
  document.querySelector('#preview').src = previewURL;
  document.querySelector('#preview-wrap').hidden = false;
  document.querySelector('#filename').textContent = file.name;
  renderButton.disabled = busy;
  setStatus('图片已选择，点击“生成可视化”。');
}

fileInput.addEventListener('change', () => selectFile(fileInput.files[0]));
sampleButton.addEventListener('click', async () => {
  setBusy(true);
  try {
    setStatus('正在读取示例图片…');
    const response = await fetch('test-images/test6.jpeg');
    if (!response.ok) throw new Error('示例图片下载失败，请重试。');
    await selectFile(new File([await response.blob()], 'test6.jpeg', { type: 'image/jpeg' }));
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    setBusy(false);
  }
});

function settingsChanged() {
  if (!selectedFile) return;
  needsRender = true;
  setStatus(plot.data
    ? '设置已更改，请重新生成。当前画布保留上次结果。'
    : '设置已更改，点击“生成可视化”。');
}

spaceInput.addEventListener('change', () => {
  document.querySelector('#space-description').textContent = {
    HSV: '观察色相、饱和度与明度的分布。',
    HSL: '观察色相、饱和度与亮度的双圆锥分布。',
    CIELCH: '观察色相、色度与感知明度的分布。',
  }[spaceInput.value];
  settingsChanged();
});
samplesInput.addEventListener('change', settingsChanged);

function createWorker() {
  const instance = new Worker('python-worker.js');
  instance.onmessage = async ({ data }) => {
    if (data.type === 'status') {
      setStatus(data.message);
    } else if (data.type === 'error') {
      console.error(data.message);
      setStatus(`处理失败：${data.message}。可换一张图片重试；若运行时加载失败，请检查网络后刷新页面。`, true);
      setBusy(false);
    } else if (data.type === 'result') {
      try {
        if (!window.Plotly) throw new Error('Plotly 未加载，请检查网络后刷新页面');
        const figure = JSON.parse(data.figure);
        // Preserve the original Python scene and reference traces.
        figure.layout.autosize = true;
        figure.layout.showlegend = false;
        figure.layout.uirevision = spaceInput.value;
        figure.layout.margin = { l: 0, r: 0, b: 0, t: 0 };
        figure.layout.title = { text: '' };
        figure.layout.paper_bgcolor = '#0a0a0a';
        figure.layout.font = { ...figure.layout.font, color: '#dce5df' };
        document.querySelector('#empty')?.remove();
        await Plotly.react(plot, figure.data, figure.layout, {
          responsive: true, displaylogo: false, scrollZoom: true,
          toImageButtonOptions: { filename: 'image-color-distribution', format: 'png' },
        });
        needsRender = false;
        document.querySelector('#view-space').textContent = spaceInput.value;
        document.querySelector('#point-count').textContent = `${data.points.toLocaleString()} 个颜色点`;
        setStatus('拖动点云可旋转视角，滚轮可缩放。');
      } catch (error) {
        setStatus(`图表显示失败：${error.message}`, true);
      } finally {
        setBusy(false);
      }
    }
  };
  instance.onerror = (error) => {
    console.error(error);
    setStatus('Python 运行时加载失败，请检查 CDN 网络连接后重试。', true);
    instance.terminate();
    worker = undefined;
    setBusy(false);
  };
  return instance;
}

renderButton.addEventListener('click', async () => {
  if (!selectedFile || busy) return;
  setBusy(true);
  setStatus('正在准备 Python 运行时，首次加载可能需要数十秒…');
  try {
    worker ??= createWorker();
    const buffer = await selectedFile.arrayBuffer();
    worker.postMessage({ buffer, space: spaceInput.value, side: Number(samplesInput.value) }, [buffer]);
  } catch (error) {
    setStatus(error.message, true);
    setBusy(false);
  }
});
