#!/usr/bin/env bash
# Chạy toàn bộ dự án: pipeline + 4 notebooks + tests
# Usage: ./run_all.sh  hoặc  bash run_all.sh

set -e  # dừng nếu có lỗi
cd "$(dirname "$0")"

echo "========================================="
echo " 1/3  Running unit tests"
echo "========================================="
python3 -m pytest tests/ -q

echo ""
echo "========================================="
echo " 2/3  Running end-to-end pipeline"
echo "========================================="
python3 -m src.pipeline

echo ""
echo "========================================="
echo " 3/3  Executing 4 notebooks"
echo "========================================="
python3 - <<'PY'
import nbformat
from nbclient import NotebookClient

notebooks = [
    "01_problem_and_data.ipynb",
    "02_collection_and_cleaning.ipynb",
    "03_eda.ipynb",
    "04_machine_learning.ipynb",
]
for nb_file in notebooks:
    print(f"--- {nb_file} ---")
    nb = nbformat.read(f"notebooks/{nb_file}", as_version=4)
    client = NotebookClient(nb, timeout=180, kernel_name="python3")
    client.execute()
    nbformat.write(nb, f"notebooks/{nb_file.replace('.ipynb', '_executed.ipynb')}")
    print("  OK")
PY

echo ""
echo "========================================="
echo " DONE. Kết quả tại:"
echo "   - reports/metrics.json"
echo "   - reports/figures/"
echo "   - reports/sample_recommendations.csv"
echo "   - reports/final_report.md"
echo "========================================="