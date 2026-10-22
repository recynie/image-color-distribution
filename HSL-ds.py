import numpy as np
import plotly.graph_objects as go
from skimage import io, transform

def rgb_to_hsl(rgb_img):
    """ 手动实现RGB到HSL颜色空间的向量化转换 """
    r, g, b = rgb_img[..., 0], rgb_img[..., 1], rgb_img[..., 2]
    
    max_val = np.max(rgb_img, axis=-1)
    min_val = np.min(rgb_img, axis=-1)
    delta = max_val - min_val
    
    # 计算亮度L
    L = (max_val + min_val) / 2
    
    # 计算饱和度S
    S = np.zeros_like(L)
    mask = (delta != 0)
    S[mask] = np.where(
        L[mask] <= 0.5,
        delta[mask] / (max_val[mask] + min_val[mask]),
        delta[mask] / (2 - max_val[mask] - min_val[mask])
    )
    
    # 计算色相H
    H = np.zeros_like(L)
    max_r = (max_val == r) & mask
    max_g = (max_val == g) & mask
    max_b = (max_val == b) & mask
    
    H[max_r] = (g[max_r] - b[max_r]) / delta[max_r] % 6
    H[max_g] = (b[max_g] - r[max_g]) / delta[max_g] + 2
    H[max_b] = (r[max_b] - g[max_b]) / delta[max_b] + 4
    H = (H / 6) % 1.0  # 归一化到[0,1)
    
    return np.stack([H, S, L], axis=-1)

# 读取图像并降采样
image = io.imread('test-images/test6.jpeg')  # 替换为你的图片路径
image_small = transform.resize(image, (100, 100), anti_aliasing=True)

# 转换为HSL颜色空间
hsl = rgb_to_hsl(image_small[..., :3])
H, S, L = hsl[..., 0], hsl[..., 1], hsl[..., 2]

# 转换为双圆锥坐标
theta = H * 2 * np.pi  # 方位角 (0-2π)
z = 2 * L - 1          # 垂直坐标 (-1到1)

# 计算半径（双圆锥结构）
radius = np.where(L <= 0.5, 
                 S * L * 2,        # 下半圆锥
                 S * (1 - L) * 2)  # 上半圆锥

x = radius * np.cos(theta)
y = radius * np.sin(theta)

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
        line=dict(width=0)
    ),
    showlegend=False  # 隐藏散点图的图例
)

# 创建双圆锥参考线
def create_cone_reference():
    # 水平纬线
    lat_lines = []
    for l in np.linspace(0.1, 0.9, 8):
        z_val = 2 * l - 1
        theta = np.linspace(0, 2 * np.pi, 100)
        r = min(l * 2, (1 - l) * 2)  # 自动适应上下圆锥
        x_lat = r * np.cos(theta)
        y_lat = r * np.sin(theta)
        lat_lines.append(go.Scatter3d(
            x=x_lat, y=y_lat, z=np.full(100, z_val),
            mode='lines', 
            line=dict(color='rgba(255,255,255,0.3)', width=1),
            showlegend=False  # 隐藏图例
        ))
    
    # 垂直经线
    lon_lines = []
    for h in np.linspace(0, 1, 12)[:-1]:
        theta = h * 2 * np.pi
        l_vals = np.linspace(0, 1, 50)
        z_lon = 2 * l_vals - 1
        r_lon = np.where(l_vals <= 0.5, l_vals * 2, (1 - l_vals) * 2)
        x_lon = r_lon * np.cos(theta)
        y_lon = r_lon * np.sin(theta)
        lon_lines.append(go.Scatter3d(
            x=x_lon, y=y_lon, z=z_lon,
            mode='lines', 
            line=dict(color='rgba(255,255,255,0.3)', width=1),
            showlegend=False  # 隐藏图例
        ))
    
    # 中央轴线
    axis_line = go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[-1, 1],
        mode='lines', 
        line=dict(color='gray', width=2),
        showlegend=False  # 隐藏图例
    )
    
    return lat_lines + lon_lines + [axis_line]

# 创建图形布局
layout = go.Layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor='rgb(10,10,10)',
        camera=dict(
            up=dict(x=0, y=0, z=1),
            eye=dict(x=1.2, y=1.2, z=0.6))),
    margin=dict(l=0, r=0, b=0, t=0),
    paper_bgcolor='rgb(10,10,10)'
)

# 组合图形元素
fig = go.Figure(data=[scatter] + create_cone_reference(), layout=layout)

# 显示交互式图形
fig.show()