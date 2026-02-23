"""Pytest configuration — ensures src/ is importable from any working directory."""
import sys
from pathlib import Path

# Add project root to sys.path so `from src.X import Y` works portably
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
