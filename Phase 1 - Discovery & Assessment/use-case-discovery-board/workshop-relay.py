#!/usr/bin/env python3
"""Compatibility launcher for the durable standalone workshop relay."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[2] / 'use-case-discovery-board/relay.py'), run_name='__main__')
