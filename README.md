# StockTech Analysis

Automated stock technical analysis & prediction system for the Vietnamese market (VN30). Crawls price data via yfinance, computes 15+ indicators, and generates buy/sell signals using a weighted voting engine with ≥70% consensus threshold.

## Features

- **Data Crawling** — fetches historical price data via yfinance
- **40+ Technical Indicators** — SMA, EMA, MACD, RSI, Stochastic RSI, Supertrend, ADX, Ichimoku, Bollinger Bands, Parabolic SAR, Aroon, Vortex, CMF, MFI, Williams %R, CCI, and more
- **Prediction Engine** — weighted voting system with configurable consensus threshold
- **Backtesting** — compare predictions against actual market performance
- **FastAPI Dashboard** — REST API for on-demand analysis
- **Telegram Bot** — automated daily alerts with buy/sell signals
- **Daily Pipeline** — scheduled via APScheduler at 2:00 AM
- **Report Generation** — Markdown, HTML, JSON output
- **Docker Support** — one-command deployment with Docker Compose
- **Design Patterns** — Strategy, Observer, Factory, Singleton, Facade

## Quick Start

### Local

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker compose up -d
```

## Configuration

Set environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | — | Telegram bot token (optional) |
| `TELEGRAM_CHAT_ID` | — | Telegram chat ID (optional) |
| `PIPELINE_HOUR` | `2` | Daily pipeline hour (UTC+7) |
| `PIPELINE_MINUTE` | `0` | Daily pipeline minute |
| `DB_PATH` | `stock_data.db` | SQLite database path |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/analyze/{symbol}` | Analyze a single symbol |
| GET | `/api/analyze/all` | Analyze all tracked symbols |
| GET | `/api/symbols` | List tracked symbols |

## Project Structure

```
├── main.py                  # FastAPI app with scheduler
├── config.py                # Configuration & constants
├── crawler.py               # Data crawling (yfinance)
├── indicators.py            # Technical indicators computation
├── predictor.py             # Weighted voting prediction engine
├── patterns.py              # Design patterns implementations
├── backtest_and_predict.py  # Combined backtest + prediction
├── enhanced_runner.py       # Enhanced runner with design patterns
├── scheduler.py             # Standalone pipeline scheduler
├── report_generator.py      # Report generation (MD/HTML/JSON)
├── telegram_bot.py          # Telegram notification bot
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── reports/                 # Generated reports
```

## Tech Stack

Python 3.11, FastAPI, Pandas, NumPy, APScheduler, python-telegram-bot, yfinance, Docker

## License

MIT
