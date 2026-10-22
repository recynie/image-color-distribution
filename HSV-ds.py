import numpy as np
import plotly.graph_objects as go
from skimage import io, transform
import matplotlib.colors as mcolors

# 读取图像并降采样
# 网页通过共享入口传入 RGB 图像；直接运行时继续使用示例图片。
image = globals().get('INPUT_IMAGE')
if image is None:
    image = io.imread('test-images/test6.jpeg')
side = globals().get('SAMPLE_SIDE', 100)
image_small = transform.resize(image, (side, side), anti_aliasing=True)

# 转换为HSV颜色空间
hsv = mcolors.rgb_to_hsv(image_small[..., :3])
H = hsv[..., 0]  # 色相 (0-1)
S = hsv[..., 1]  # 饱和度 (0-1)
V = hsv[..., 2]  # 明度 (0-1)

# 转换为3D球坐标
phi = H * 2 * np.pi        # 方位角 (0-2π)
z = 2 * V - 1              # 垂直坐标 (-1到1)
max_r = np.sin(V * np.pi)  # 最大投影半径
r = S * max_r              # 实际投影半径

x = r * np.cos(phi)
y = r * np.sin(phi)

# 获取颜色信息
colors = image_small[..., :3].reshape(-1, 3)

# 创建3D散点图
scatter = go.Scatter3d(
    x=x.flatten(),
    y=y.flatten(),
    z=z.flatten(),
    mode='markers',
    marker=dict(
        size=3,
        color=colors,
        opacity=0.7,
        line=dict(width=0))
)

# 创建球体参考线
def create_reference_lines():
    # 纬度圈
    lat_lines = []
    for v in np.linspace(0.1, 0.9, 4):
        z_val = 2*v - 1
        theta = np.linspace(0, 2*np.pi, 100)
        r_val = np.sin(v*np.pi)
        x_lat = r_val * np.cos(theta)
        y_lat = r_val * np.sin(theta)
        lat_lines.append(go.Scatter3d(
            x=x_lat, y=y_lat, z=np.full(100, z_val),
            mode='lines', line=dict(color='white', width=1)))
    
    # 经线
    lon_lines = []
    for h in np.linspace(0, 1, 5)[:-1]:
        phi_lon = h * 2 * np.pi
        v_vals = np.linspace(0, 1, 50)
        z_lon = 2*v_vals - 1
        r_lon = np.sin(v_vals*np.pi)
        x_lon = r_lon * np.cos(phi_lon)
        y_lon = r_lon * np.sin(phi_lon)
        lon_lines.append(go.Scatter3d(
            x=x_lon, y=y_lon, z=z_lon,
            mode='lines', line=dict(color='white', width=1)))
    
    # 中央轴线
    axis_line = go.Scatter3d(
        x=[0,0], y=[0,0], z=[-1,1],
        mode='lines', line=dict(color='gray', width=2))
    
    return lat_lines + lon_lines + [axis_line]

# 创建图形布局
layout = go.Layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor='rgb(10,10,10)',
        camera=dict(up=dict(x=0, y=0, z=1),
                    eye=dict(x=1.5, y=1.5, z=0.5))),
    margin=dict(l=0, r=0, b=0, t=0),
    paper_bgcolor='rgb(10,10,10)'
)

# 组合所有元素
fig = go.Figure(data=[scatter] + create_reference_lines(), layout=layout)

# 显示交互式图形
if globals().get('SHOW_FIGURE', True):
    fig.show()