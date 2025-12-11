"""
Code Gen AI - Modular Entry Point

Run with: streamlit run run.py
"""

import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from code_gen_ai.app import main

if __name__ == "__main__":
    main()
