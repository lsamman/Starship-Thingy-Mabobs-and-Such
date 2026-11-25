"""Faired HLS landing leg: the same leg in white, slim enough for the 2024 style's pods."""
import os
WHITE = True
exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_hlsleg.py")).read(), "build_hlsleg.py", "exec"))
