"""
Script phân tích toàn diện — delegate to enhanced_runner.
Giữ lại để tương thích ngược.
"""
import asyncio
from enhanced_runner import AnalysisFacade
from config import DEFAULT_SYMBOLS


async def main():
    facade = AnalysisFacade(
        symbols=["ACB", "VCB", "FPT", "HPG", "MWG"],
        observers=["telegram", "file"],
    )
    await facade.run()


if __name__ == "__main__":
    asyncio.run(main())
