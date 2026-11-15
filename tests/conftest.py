import pathlib
import sys

# 让测试直接 import fanbox_core / fanbox_api（它们不依赖 AstrBot）。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
