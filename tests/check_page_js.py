# check_page_js.py — extract the page script and run node --check on it.

import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "index.html").read_text()
scripts = re.findall(r"<script>(.*?)</script>", src, re.S)
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
    fh.write("\n".join(scripts))
    path = fh.name
try:
    subprocess.run(["node", "--check", path], check=True)
finally:
    pathlib.Path(path).unlink(missing_ok=True)
print("page script parses")
