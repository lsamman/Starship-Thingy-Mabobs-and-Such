"""Aeroshielded landing leg for SEP's Block 3 ship: the HLS leg with a shell over it."""
import os
SHIP = True
exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_hlsleg.py")).read(), "build_hlsleg.py", "exec"))
