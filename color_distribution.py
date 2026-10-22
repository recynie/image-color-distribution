"""Shared browser/desktop entry point for the existing visualization scripts."""

from pathlib import Path
import runpy

import numpy as np


SCRIPTS = {"HSV": "HSV-ds.py", "HSL": "HSL-ds.py", "CIELCH": "CIELCH-ds.py"}


def build_figure(rgb_image, space="HSV", sample_side=100):
    """Build a Plotly figure using the original Python calculations and layout.

    rgb_image is an H×W×3 uint8 array. sample_side bounds the cloud to
    sample_side² points. This adapter runs scripts without opening a browser.
    """
    if space not in SCRIPTS:
        raise ValueError(f"Unsupported color space: {space}")
    if sample_side not in (50, 100, 150):
        raise ValueError("sample_side must be 50, 100, or 150")
    image = np.asarray(rgb_image)
    if image.ndim != 3 or image.shape[2] != 3 or image.dtype != np.uint8:
        raise ValueError("Expected an H×W×3 uint8 RGB image")
    namespace = runpy.run_path(
        str(Path(__file__).parent / SCRIPTS[space]),
        init_globals={
            "INPUT_IMAGE": image,
            "SAMPLE_SIDE": sample_side,
            "MAX_SAMPLES": sample_side**2,
            "SHOW_FIGURE": False,
        },
    )
    fig = namespace["fig"]
    # Plotly.js expects CSS color strings for each point, not an N×3 array.
    colors = np.asarray(fig.data[0].marker.color)
    if colors.ndim == 2 and colors.shape[1] == 3:
        colors = np.rint(np.clip(colors, 0, 1) * 255).astype(np.uint8)
        fig.data[0].marker.color = [
            f"rgb({r},{g},{b})" for r, g, b in colors
        ]
    return fig
