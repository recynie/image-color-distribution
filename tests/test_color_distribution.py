import unittest
from unittest.mock import patch

import numpy as np
import plotly.graph_objects as go

from color_distribution import build_figure


class ColorDistributionTest(unittest.TestCase):
    def test_all_spaces_reuse_scripts_without_opening_browser(self):
        image = np.zeros((60, 70, 3), dtype=np.uint8)
        image[:, :35] = [255, 0, 0]
        image[:, 35:] = [0, 255, 0]
        for space, trace_count in [('HSV', 10), ('HSL', 21), ('CIELCH', 24)]:
            with self.subTest(space=space), patch.object(go.Figure, 'show') as show:
                fig = build_figure(image, space, 50)
                show.assert_not_called()
                self.assertEqual(len(fig.data), trace_count)
                self.assertLessEqual(len(fig.data[0].x), 2500)
                self.assertTrue(all(c.startswith('rgb(') for c in fig.data[0].marker.color))
                fig.to_json()

    def test_invalid_parameters(self):
        image = np.zeros((2, 2, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            build_figure(image, 'unknown')
        with self.assertRaises(ValueError):
            build_figure(image, sample_side=1)
        with self.assertRaises(ValueError):
            build_figure(np.zeros((2, 2)))


if __name__ == '__main__':
    unittest.main()
