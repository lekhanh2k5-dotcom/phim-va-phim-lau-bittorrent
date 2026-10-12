"""Dựng notebook từ một file nguồn .py chia khối '# ---- NN. ...' + nội dung markdown.

    build(src_py, out_ipynb, intro_md, cells_md: {NN: (question_md, note_md)}, summary_md)
Khối đầu (trước '# ---- 01.') thành ô 'Nạp dữ liệu'. Sau đó chạy notebook để lưu sẵn kết quả.
"""
import re
from pathlib import Path

import nbformat
from nbclient import NotebookClient

SETUP = '''# Tìm thư mục gốc dự án (chứa src/viz_style.py) để import phong cách biểu đồ dùng chung
import sys
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src" / "viz_style.py").exists())
sys.path.insert(0, str(ROOT / "src"))
%matplotlib inline'''


def build(src_py, out_ipynb, intro_md, cells_md, summary_md):
    src = Path(src_py).read_text(encoding="utf-8")
    body = src.split('"""', 2)[2] if src.lstrip().startswith('"""') else src
    blocks = re.split(r"\n(?=# ---- \d\d\. )", body)
    head, charts = blocks[0].strip(), blocks[1:]
    cells = [nbformat.v4.new_markdown_cell(intro_md), nbformat.v4.new_code_cell(SETUP),
             nbformat.v4.new_markdown_cell("## Nạp dữ liệu"), nbformat.v4.new_code_cell(head)]
    for blk in charts:
        num = re.match(r"# ---- (\d\d)\.", blk).group(1)
        q, note = cells_md[num]
        cells += [nbformat.v4.new_markdown_cell(q),
                  nbformat.v4.new_code_cell(re.sub(r"^# ---- .*\n", "", blk).strip()),
                  nbformat.v4.new_markdown_cell(note)]
    cells.append(nbformat.v4.new_markdown_cell(summary_md))
    nb = nbformat.v4.new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    out = Path(out_ipynb)
    NotebookClient(nb, timeout=1800, kernel_name="python3",
                   resources={"metadata": {"path": str(out.parent)}}).execute()
    nbformat.write(nb, out)
    imgs = sum("image/png" in o.get("data", {}) for c in nb.cells if c.cell_type == "code" for o in c.outputs)
    print(f"wrote {out} ({imgs} hình)")
