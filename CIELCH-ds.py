import numpy as np
from PIL import Image
import plotly.graph_objects as go
from skimage.color import rgb2lab

# 读取图像并转换为RGB数组
image_path = 'test-images/test2.jpeg'  # 替换为你的图片路径
img = Image.open(image_path).convert('RGB')
img_rgb = np.array(img)

# 转换为CIELAB色彩空间
img_lab = rgb2lab(img_rgb)
L = img_lab[:, :, 0]
a = img_lab[:, :, 1]
b = img_lab[:, :, 2]

# 计算色度(Chroma)和色相(Hue)
C = np.sqrt(a**2 + b**2)
h_rad = np.arctan2(b, a)  # 弧度制角度（-π到π）
h_deg = np.degrees(h_rad) % 360  # 转换为0-360度

# 展平数组并降采样
height, width = img_rgb.shape[:2]
num_pixels = height * width
max_samples = 2000
step_size = max(1, num_pixels // max_samples)

# 创建采样掩码
xx, yy = np.meshgrid(np.arange(width), np.arange(height))
indices = yy * width + xx
sampled_indices = indices.flatten()[::step_size]

# 提取采样数据
L_flat = L.flatten()[sampled_indices]
C_flat = C.flatten()[sampled_indices]
h_rad_flat = h_rad.flatten()[sampled_indices]
colors = img_rgb.reshape(-1, 3)[sampled_indices]

# 转换为圆柱坐标
x = C_flat * np.cos(h_rad_flat)  # 色度在极坐标中的X分量
y = C_flat * np.sin(h_rad_flat)  # 色度在极坐标中的Y分量
z = L_flat                      # 明度作为高度

# 创建圆柱体可视化
fig = go.Figure()

# 添加颜色点云
fig.add_trace(go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
        size=3,
        color=colors/255,
        opacity=0.9,
        line=dict(width=0)
    ),
    hovertemplate=
    '<b>Hue</b>: %{text[0]:.1f}°<br>' +
    '<b>Chroma</b>: %{text[1]:.1f}<br>' +
    '<b>Lightness</b>: %{z:.1f}<extra></extra>',
    text=np.stack([h_deg.flatten()[sampled_indices], C_flat], axis=1)
))

# 计算最大色度用于圆柱体轮廓
max_chroma = C_flat.max() * 1.1

# 添加圆柱体轮廓线
theta = np.linspace(0, 2*np.pi, 100)  # 角度范围
z_levels = np.linspace(0, 100, 5)    # 明度分层

# 添加圆柱体侧面轮廓线
for z_val in z_levels:
    x_cyl = max_chroma * np.cos(theta)
    y_cyl = max_chroma * np.sin(theta)
    fig.add_trace(go.Scatter3d(
        x=x_cyl,
        y=y_cyl,
        z=np.full_like(theta, z_val),
        mode='lines',
        line=dict(color='white', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

# 添加圆柱体顶部和底部轮廓线
for z_val in [0, 100]:
    x_cyl = max_chroma * np.cos(theta)
    y_cyl = max_chroma * np.sin(theta)
    fig.add_trace(go.Scatter3d(
        x=x_cyl,
        y=y_cyl,
        z=np.full_like(theta, z_val),
        mode='lines',
        line=dict(color='white', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

# 添加垂直轮廓线
for angle in np.linspace(0, 2*np.pi, 6):  # 每30度一条垂直线
    x_line = [max_chroma * np.cos(angle), max_chroma * np.cos(angle)]
    y_line = [max_chroma * np.sin(angle), max_chroma * np.sin(angle)]
    z_line = [0, 100]
    fig.add_trace(go.Scatter3d(
        x=x_line,
        y=y_line,
        z=z_line,
        mode='lines',
        line=dict(color='white', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

# 添加顶面和底面的同心圆
for r in np.linspace(0, max_chroma, 6)[1:]:  # 从内到外添加同心圆
    for z_val in [0, 100]:
        x_circle = r * np.cos(theta)
        y_circle = r * np.sin(theta)
        fig.add_trace(go.Scatter3d(
            x=x_circle,
            y=y_circle,
            z=np.full_like(theta, z_val),
            mode='lines',
            line=dict(color='white', width=1, dash='dot'),
            showlegend=False,
            hoverinfo='skip'
        ))

# 优化布局
fig.update_layout(
    title='Cylindrical CIELCH Color Space',
    scene=dict(
        xaxis=dict(visible=False),  # 隐藏X轴
        yaxis=dict(visible=False),  # 隐藏Y轴
        zaxis=dict(visible=False),  # 隐藏Z轴
        aspectmode='manual',
        aspectratio=dict(x=1, y=1, z=1),
        camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=0),
            eye=dict(x=1.5, y=1.5, z=0.8)
        ),
        bgcolor='black'  # 背景设为黑色
    ),
    margin=dict(l=0, r=0, b=0, t=30),
    font=dict(family="Arial", size=12, color='white')  # 字体颜色设为白色
)

# 显示图表
fig.show()

# 保存为HTML文件
# fig.write_html("cielch_cylinder_outline_black.html")