"""Cronjob — delegate to enhanced_runner."""
from enhanced_runner import run_pipeline_sync as _run_pipeline

if __name__ == "__main__":
    _run_pipeline()
