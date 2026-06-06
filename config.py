import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = Path(os.getenv("DB_PATH", str(BASE_DIR / "stock_data.db")))

# Danh sách mã cổ phiếu theo dõi (mặc định VN30)
DEFAULT_SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR",
    "HDB", "HPG", "MBB", "MSN", "MWG", "NVL", "PLX", "POW",
    "SAB", "SBT", "SHB", "SSI", "STB", "TCB", "TPB", "VCB",
    "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE",
]

# Nguồn dữ liệu: "vndirect" hoặc "cafef"
DATA_SOURCE = "yfinance"

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# FastAPI
API_HOST = "0.0.0.0"
API_PORT = 8000

# Thời gian chạy pipeline (giờ phút)
PIPELINE_HOUR = int(os.getenv("PIPELINE_HOUR", "2"))
PIPELINE_MINUTE = int(os.getenv("PIPELINE_MINUTE", "0"))

# Số ngày dữ liệu tối thiểu
MIN_DATA_DAYS = 100
# Số ngày crawl mỗi lần
FETCH_DAYS = 365
