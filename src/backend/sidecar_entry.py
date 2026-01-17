#!/usr/bin/env python3
"""Entry point for PyInstaller sidecar build.

This script is the entry point for building a standalone sidecar binary.
It uses absolute imports to avoid import issues with PyInstaller.
"""

import sys
import os

# Add src directory to path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled
    pass
else:
    # Running in normal Python
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# Now import and run the sidecar main function
from backend.sidecar import main

if __name__ == "__main__":
    main()
