#!/bin/bash
# Script chạy pipeline phân tích kỹ thuật - gọi bởi cronjob 2h sáng
# Đường dẫn: /Users/tonyson/Desktop/TuanAnh/run_pipeline.sh

cd /Users/tonyson/Desktop/TuanAnh || exit 1

source venv/bin/activate 2>/dev/null || true

python3 -c "
import asyncio
from scheduler import run_pipeline
asyncio.run(run_pipeline())
" >> pipeline.log 2>&1

echo "[$(date)] Pipeline completed" >> pipeline.log
