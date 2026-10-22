#!/bin/python3
import cv2
import numpy as np
import plotly.graph_objects as go

IMG='test-images/test1.jpeg'
SPHERE=False


# 加载图像并下采样
image = cv2.imread(IMG)
image = cv2.resize(image, (100, 100))  # 下采样

# 将图像从 BGR 转换为 HSV
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
h, s, v = cv2.split(hsv_image)

# 转换为笛卡尔坐标
def hsv_to_cartesian(h, s, v):
    theta = np.deg2rad(h)
    r = s / 255.0 * v / 255.0
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = v / 255.0
    return x, y, z

# 创建散点图数据
x_vals, y_vals, z_vals = [], [], []
colors = []  # 用于存储颜色

for i in range(h.shape[0]):
    for j in range(h.shape[1]):
        x, y, z = hsv_to_cartesian(h[i][j], s[i][j], v[i][j])
        x_vals.append(x)
        y_vals.append(y)
        z_vals.append(z)
        
        # 添加对应的 BGR 颜色，并转换为 RGB
        b, g, r = image[i, j]
        colors.append(f'rgba({r}, {g}, {b}, 1)')  # 添加透明度

# 创建球面
def create_sphere(radius, detail=20):
    u = np.linspace(0, 2 * np.pi, detail)
    v = np.linspace(0, np.pi, detail)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    return x, y, z


if SPHERE:
    # 创建球面数据
    sphere_x, sphere_y, sphere_z = create_sphere(1)
    # 创建球面图
    sphere_trace = go.Mesh3d(
        x=sphere_x.flatten(), 
        y=sphere_y.flatten(), 
        z=sphere_z.flatten(),
        opacity=0.1,
        color='lightblue',
        alphahull=0
    )

# 创建 3D 散点图
scatter_trace = go.Scatter3d(
    x=x_vals, y=y_vals, z=z_vals,
    mode='markers',
    marker=dict(
        size=3,
        color=colors,  # 使用图像中的颜色
        opacity=0.8
    )
)


#todo 设置背景色为图像中没有的颜色
r=g=b=a=0
bg_color=f'rgba({r},{g},{b},{a})'


# 创建图表布局，隐藏坐标系和背景
layout = go.Layout(
    title="Interactive HSV Color Sphere",
    scene=dict(
        xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showline=False, showticklabels=False, title=None),
        yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showline=False, showticklabels=False, title=None),
        zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showline=False, showticklabels=False, title=None),
        bgcolor='rgba(0, 0, 0, 0)',  # 设置背景为透明
        aspectmode='cube',
        annotations=[],  # 清空注释，隐藏坐标轴标签
    ),
    paper_bgcolor=bg_color,  # 设置纸张背景为透明
    plot_bgcolor=bg_color    # 设置绘图背景为透明
)
        
# 可视化色球
d=[scatter_trace, sphere_trace] if SPHERE else [scatter_trace]
fig = go.Figure(data=d, layout=layout)
fig.show()
