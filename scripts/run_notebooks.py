"""Execute 4 notebooks của đồ án, ghi *_executed.ipynb.

Chạy:
    python3 scripts/run_notebooks.py
"""

from __future__ import annotations

import nbformat
from nbclient import NotebookClient

NOT_DIR = "notebooks"

NOTEBOOKS = [
    "01_problem_and_data.ipynb",
    "02_collection_and_cleaning.ipynb",
    "03_eda.ipynb",
    "04_machine_learning.ipynb",
]


def main() -> None:
    for nb_file in NOTEBOOKS:
        path = f"{NOT_DIR}/{nb_file}"
        print(f"--- {nb_file} ---")
        nb = nbformat.read(path, as_version=4)
        client = NotebookClient(nb, timeout=180, kernel_name="python3")
        client.execute()
        out = path.replace(".ipynb", "_executed.ipynb")
        nbformat.write(nb, out)
        print(f"  OK → {out}")


if __name__ == "__main__":
    main()
