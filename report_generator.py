"""Report Generator - Strategy pattern for report output.

Generates:
- Markdown report
- HTML report with styling
- JSON data export
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _extract_trends(self, result: Dict[str, Any]) -> Dict[str, Any]:
        pred = result.get("prediction", {})
        trend = pred.get("trend", {})
        signals = pred.get("signals", {})
        meta = pred.get("metadata", {})
        bt = result.get("backtest", {})
        return {
            "symbol": result.get("symbol"),
            "last_close": result.get("last_close"),
            "last_date": result.get("last_date"),
            "data_points": result.get("data_points"),
            "short_term": trend.get("ngan_han_1_5_ngay", "N/A"),
            "medium_term": trend.get("trung_han_5_20_ngay", "N/A"),
            "long_term": trend.get("dai_han_20_50_ngay", "N/A"),
            "rsi": meta.get("rsi_14"),
            "macd": signals.get("macd", "N/A"),
            "adx": signals.get("adx_strength", "N/A"),
            "adx_dir": signals.get("adx_direction", "N/A"),
            "ichimoku": signals.get("ichimoku", "N/A"),
            "supertrend": signals.get("supertrend", "N/A"),
            "mfi": meta.get("mfi_14"),
            "volume_osc": meta.get("volume_osc"),
            "choppiness": meta.get("choppiness_14"),
            "entry_advice": pred.get("entry_advice", "N/A"),
            "backtest_accuracy": bt.get("accuracy", 0),
            "backtest_correct": bt.get("correct", 0),
            "backtest_total": bt.get("total", 0),
            "backtest_tests": bt.get("tests", []),
        }

    def generate_markdown(self, results: List[Dict[str, Any]]) -> str:
        lines = [
            f"# Báo Cáo Phân Tích Kỹ Thuật — {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "",
            f"**Tổng số mã phân tích:** {len(results)}",
            "",
            "---",
            "",
            "## Mục Lục",
            "",
        ]
        for i, r in enumerate(results):
            sym = r.get("symbol", "N/A")
            lines.append(f"{i+1}. [{sym}](#{sym.lower()})")
        lines.append("")

        for r in results:
            data = self._extract_trends(r)
            lines.extend(self._format_symbol_md(data))

        filepath = os.path.join(self.output_dir, f"report_{self.timestamp}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Also save to the fixed test_report.md
        test_path = os.path.join(os.path.dirname(self.output_dir), "test_report.md")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"  📄 Markdown report: {filepath}")
        return filepath

    def _format_symbol_md(self, d: Dict[str, Any]) -> List[str]:
        lines = [
            f"<a name='{d['symbol'].lower()}'></a>",
            f"## {d['symbol']} — Giá: {d['last_close']:,.0f}₫",
            "",
            f"**Ngày cuối:** {d['last_date']} | **Số phiên:** {d['data_points']}",
            "",
            "### Xu Hướng",
            f"| Thời gian | Xu hướng |",
            "|-----------|----------|",
            f"| Ngắn hạn (1-5 ngày) | {d['short_term']} |",
            f"| Trung hạn (5-20 ngày) | {d['medium_term']} |",
            f"| Dài hạn (20-50 ngày) | {d['long_term']} |",
            "",
            "### Chỉ Báo Chính",
            f"- **RSI(14):** {d.get('rsi', 'N/A')}",
            f"- **MACD:** {d['macd']}",
            f"- **ADX:** {d['adx']} / Hướng: {d['adx_dir']}",
            f"- **Ichimoku:** {d['ichimoku']}",
            f"- **Supertrend:** {d['supertrend']}",
            f"- **MFI(14):** {d.get('mfi', 'N/A')}",
            "",
            f"### Gợi ý Giao Dịch",
            f"> **{d['entry_advice']}**",
            "",
        ]

        if d["backtest_total"] > 0:
            acc = d["backtest_accuracy"]
            bar = "🟢" if acc >= 60 else "🟡" if acc >= 40 else "🔴"
            lines.extend([
                "### Backtest",
                f"{bar} Độ chính xác: {d['backtest_correct']}/{d['backtest_total']} ({acc:.0f}%)",
                "",
                "| Ngày | Dự đoán | Thực tế | Thay đổi | Kết quả |",
                "|------|---------|---------|----------|---------|",
            ])
            for t in d["backtest_tests"][-10:]:
                icon = "✅" if t["correct"] else "❌"
                pct = t["change_pct"]
                sign = "+" if pct > 0 else ""
                lines.append(
                    f"| {t['date']} | {t['predicted']} | {t['direction']} "
                    f"| {sign}{pct:.1f}% | {icon} |"
                )
            lines.append("")

        lines.extend([
            "### Chỉ Báo Chi Tiết",
            "```",
        ])

        bt = d.get("backtest_tests", [])
        if bt:
            last = bt[-1] if bt else {}
            lines.append(f"Prev Close: {last.get('prev_close', 'N/A')}")
            lines.append(f"Actual Close: {last.get('actual_close', 'N/A')}")

        lines.append("```")
        lines.append("---")
        lines.append("")
        return lines

    def generate_html(self, results: List[Dict[str, Any]]) -> str:
        rows_html = ""
        for r in results:
            data = self._extract_trends(r)
            acc = data["backtest_accuracy"]
            acc_color = "green" if acc >= 60 else "orange" if acc >= 40 else "red"
            arrow_up = "🟢" if "TĂNG" in data["short_term"] or "MUA" in data["short_term"] else ""

            backtest_rows = ""
            for t in data["backtest_tests"][-5:]:
                icon = "✅" if t["correct"] else "❌"
                pct = t["change_pct"]
                backtest_rows += f"<tr><td>{t['date']}</td><td>{t['predicted']}</td><td>{t['direction']}</td><td>{pct:.1f}%</td><td>{icon}</td></tr>"

            rows_html += f"""
            <div class="card">
                <div class="card-header {acc_color}">
                    <h2>{data['symbol']} — {data['last_close']:,.0f}₫ <span class="arrow">{arrow_up}</span></h2>
                    <span class="date">{data['last_date']} | {data['data_points']} phiên</span>
                </div>
                <div class="card-body">
                    <div class="grid-3">
                        <div class="trend-box">
                            <h4>Xu Hướng</h4>
                            <p><strong>Ngắn hạn:</strong> {data['short_term']}</p>
                            <p><strong>Trung hạn:</strong> {data['medium_term']}</p>
                            <p><strong>Dài hạn:</strong> {data['long_term']}</p>
                        </div>
                        <div class="indicator-box">
                            <h4>Chỉ Báo</h4>
                            <p>RSI(14): {data['rsi']} | MACD: {data['macd']}</p>
                            <p>ADX: {data['adx']} / {data['adx_dir']}</p>
                            <p>Ichimoku: {data['ichimoku']}</p>
                            <p>Supertrend: {data['supertrend']}</p>
                            <p>MFI(14): {data['mfi']}</p>
                        </div>
                        <div class="advice-box">
                            <h4>Gợi ý</h4>
                            <p class="advice-text">{data['entry_advice']}</p>
                            <h4>Backtest</h4>
                            <p class="accuracy" style="color:{acc_color};font-size:1.2em;">
                                {data['backtest_correct']}/{data['backtest_total']} ({acc:.0f}%)
                            </p>
                        </div>
                    </div>
                    {f'''
                    <h4>Backtest Chi Tiết</h4>
                    <table>
                        <tr><th>Ngày</th><th>Dự đoán</th><th>Thực tế</th><th>Thay đổi</th><th>KQ</th></tr>
                        {backtest_rows}
                    </table>
                    ''' if backtest_rows else ''}
                </div>
            </div>
            """

        html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockTech Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: #0f1923; color: #e0e6ed; padding: 20px; }}
        h1 {{ text-align: center; color: #00d4aa; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #8899aa; margin-bottom: 30px; }}
        .card {{ background: #1a2d3d; border-radius: 12px; margin-bottom: 24px;
                 overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
        .card-header {{ padding: 16px 20px; display: flex; justify-content: space-between;
                       align-items: center; }}
        .card-header.green {{ background: linear-gradient(135deg, #1a5c3a, #1a2d3d); }}
        .card-header.orange {{ background: linear-gradient(135deg, #5c4a1a, #1a2d3d); }}
        .card-header.red {{ background: linear-gradient(135deg, #5c1a1a, #1a2d3d); }}
        .card-header h2 {{ font-size: 1.3em; }}
        .card-header .arrow {{ font-size: 1.5em; }}
        .card-header .date {{ color: #8899aa; font-size: 0.85em; }}
        .card-body {{ padding: 20px; }}
        .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px;
                   margin-bottom: 20px; }}
        @media (max-width: 768px) {{ .grid-3 {{ grid-template-columns: 1fr; }} }}
        .trend-box, .indicator-box, .advice-box {{ background: #243b4d;
            padding: 14px; border-radius: 8px; }}
        h4 {{ color: #00d4aa; margin-bottom: 10px; font-size: 0.95em; }}
        p {{ margin-bottom: 6px; font-size: 0.9em; line-height: 1.5; }}
        .advice-text {{ color: #f0c060; font-weight: bold; }}
        .accuracy {{ font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85em; }}
        th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #2a4050; }}
        th {{ background: #1a2d3d; color: #00d4aa; }}
        tr:hover {{ background: #2a4050; }}
        .footer {{ text-align: center; color: #556677; padding: 20px; font-size: 0.85em; }}
    </style>
</head>
<body>
    <h1>📊 StockTech Analysis Report</h1>
    <p class="subtitle">{datetime.now().strftime('%d/%m/%Y %H:%M')} | {len(results)} mã phân tích</p>
    {rows_html}
    <div class="footer">
        <p>StockTech Analysis Engine v2.0 — 40+ chỉ báo kỹ thuật</p>
        <p>Xu hướng • Động lượng • Biến động • Khối lượng • Phân kỳ</p>
    </div>
</body>
</html>"""

        filepath = os.path.join(self.output_dir, f"report_{self.timestamp}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  📄 HTML report: {filepath}")
        return filepath

    def generate_json(self, results: List[Dict[str, Any]]) -> str:
        data = [self._extract_trends(r) for r in results]
        filepath = os.path.join(self.output_dir, f"data_{self.timestamp}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"  📄 JSON data: {filepath}")
        return filepath
