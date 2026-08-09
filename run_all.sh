#!/usr/bin/env bash
# Chạy toàn bộ dự án: pipeline + 4 notebooks + tests
# Usage: ./run_all.sh  hoặc  bash run_all.sh

set -e
cd "$(dirname "$0")"

# Set env var để joblib/loky không cố detect CPU cores (gây warning/có thể
# khiến kernel jupyter bị Abort trap trên một số sandbox).
export LOKY_MAX_CPU_COUNT=${LOKY_MAX_CPU_COUNT:-4}

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
python3 scripts/run_notebooks.py

echo ""
echo "========================================="
echo " DONE. Kết quả tại:"
echo "   - reports/metrics.json"
echo "   - reports/figures/"
echo "   - reports/sample_recommendations.csv"
echo "   - reports/final_report.md"
echo "========================================="
