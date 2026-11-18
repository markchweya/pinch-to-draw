"""Double-click to start Pinch to Draw (runs without a console window)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pinch_to_draw.app import main  # noqa: E402

main()
