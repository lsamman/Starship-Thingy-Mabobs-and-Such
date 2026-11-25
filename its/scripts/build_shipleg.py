"""Landing leg for SEP's Block 3 ship: the HLS leg in bare steel, narrower at the foot."""
import os
SHIP = True
exec(compile(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_hlsleg.py")).read(), "build_hlsleg.py", "exec"))
