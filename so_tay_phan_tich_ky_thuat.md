# SỔ TAY 100+ CÔNG THỨC PHÂN TÍCH KỸ THUẬT

**SMA, EMA, RSI, ATR, MACD, Ichimoku, Bollinger Bands, ADX, OBV, Fibonacci và hơn thế nữa.**

**Mục tiêu:** tra cứu nhanh, đọc công thức nhanh, áp dụng nhanh.

---

## 📖 Cách dùng

Tài liệu này chia theo nhóm để bạn không bị ngợp khi tra cứu. 
Mỗi công thức có 3 phần: **công thức, ý nghĩa, ví dụ ngắn**.

> [!TIP]
> Nếu cần giao dịch thực chiến, hãy ghép ít nhất **1 chỉ báo xu hướng**, **1 chỉ báo động lượng** và **1 chỉ báo biến động**. 
> - **RSI** thường dùng chu kỳ 14 và vùng 70/30 để nhận biết quá mua/quá bán.
> - **Ichimoku** cung cấp cùng lúc xu hướng, động lượng và hỗ trợ/kháng cự.

---

## 1️⃣ Công thức nền tảng

### SMA (Simple Moving Average)
*   **Công thức:** SMA = (∑ P_i) / n
*   **Ý nghĩa:** Giá trung bình của n phiên.
*   **Ví dụ:** 100, 102, 101, 103, 104 → SMA_5 = 102.

### EMA (Exponential Moving Average)
*   **Công thức:** EMA_t = Price_t × k + EMA_t-1 × (1 - k), với hệ số k = 2 / (n+1)
*   **Ý nghĩa:** Ưu tiên giá gần nhất.
*   **Ví dụ:** EMA_5, giá hôm nay 105, EMA hôm qua 102 → xấp xỉ 103.

### WMA (Weighted Moving Average)
*   **Công thức:** WMA = [∑(P_i × w_i)] / (∑ w_i)
*   **Ý nghĩa:** Trọng số càng gần hiện tại càng lớn.
*   **Ví dụ:** Trọng số 1, 2, 3 cho giá 100, 102, 101.

### SMMA (Smoothed Moving Average)
*   **Công thức:** SMMA_t = [SMMA_t-1 × (n-1) + P_t] / n
*   **Ý nghĩa:** Trung bình làm mịn, ít nhiễu hơn SMA.

### VWAP (Volume Weighted Average Price)
*   **Công thức:** VWAP = [∑(Typical Price × Volume)] / (∑ Volume), với Typical Price = (H + L + C) / 3
*   **Ý nghĩa:** Giá trung bình theo khối lượng trong phiên.

### VWMA (Volume Weighted Moving Average)
*   **Công thức:** VWMA = [∑(Price × Volume)] / (∑ Volume)
*   **Ý nghĩa:** Trung bình giá có trọng số theo volume.

### Median Price
*   **Công thức:** Median = (H + L) / 2
*   **Ý nghĩa:** Giá giữa biên độ phiên.

### Typical Price
*   **Công thức:** TP = (H + L + C) / 3
*   **Ý nghĩa:** Giá “điển hình” của phiên.

### Weighted Close
*   **Công thức:** WC = (H + L + 2C) / 4
*   **Ý nghĩa:** Ưu tiên giá đóng cửa hơn.

### Price Rate of Change (ROC nền)
*   **Công thức:** ROC = [(C_t - C_t-n) / C_t-n] × 100%
*   **Ý nghĩa:** Đo tốc độ thay đổi giá.

---

## 2️⃣ Động lượng (Momentum)

### RSI (Relative Strength Index)
*   **Công thức:** RS = AvgGain / AvgLoss | RSI = 100 - [100 / (1 + RS)]
*   **Ý nghĩa:** Đo sức mạnh tương đối của giá. RSI là một trong những chỉ báo cơ bản nhất và thường được đọc với mốc 70/30.
*   **Ví dụ:** RS = 3 → RSI = 75.

### Stochastic %K
*   **Công thức:** %K = [(C - L_n) / (H_n - L_n)] × 100
*   **Ý nghĩa:** Vị trí giá hiện tại trong biên độ n phiên.

### Stochastic %D
*   **Công thức:** %D = SMA(%K, 3)
*   **Ý nghĩa:** Đường tín hiệu của Stochastic (Trung bình làm mịn của %K).

### Stochastic RSI
*   **Công thức:** StochRSI = [(RSI - Min(RSI_n)) / (Max(RSI_n) - Min(RSI_n))] × 100
*   **Ý nghĩa:** RSI được “chuẩn hóa” thêm một lớp.

### MACD (Moving Average Convergence Divergence)
*   **Công thức:** 
    *   MACD = EMA_12 - EMA_26
    *   Signal = EMA_9(MACD)
    *   Histogram = MACD - Signal
*   **Ý nghĩa:** Kết hợp xu hướng và động lượng.

### Momentum (MOM)
*   **Công thức:** MOM = Close_t - Close_t-n
*   **Ý nghĩa:** Đo độ mạnh của chuyển động giá.

### ROC (Rate of Change)
*   **Công thức:** ROC = [(Close_t - Close_t-n) / Close_t-n] × 100%
*   **Ý nghĩa:** Tốc độ biến thiên theo %.

### Williams %R
*   **Công thức:** %R = [(H_n - C) / (H_n - L_n)] × (-100)
*   **Ý nghĩa:** Tương tự Stochastic nhưng ở thang âm (-100 đến 0).

### CCI (Commodity Channel Index)
*   **Công thức:** CCI = (TP - SMA(TP, n)) / (0.015 × MeanDeviation)
*   **Ý nghĩa:** Đo độ lệch giá so với mức trung bình.

### TRIX
*   **Công thức:** Tốc độ thay đổi của EMA đã làm mịn 3 lần.
*   **Ý nghĩa:** Lọc nhiễu mạnh, dùng cho trend dài hơn.

### Ultimate Oscillator
*   **Công thức:** Kết hợp 3 khung thời gian khác nhau của buying pressure và true range.
*   **Ý nghĩa:** Giảm sai lệch do chỉ nhìn một chu kỳ.

### CMO (Chande Momentum Oscillator)
*   **Công thức:** CMO = [(∑Gains - ∑Losses) / (∑Gains + ∑Losses)] × 100
*   **Ý nghĩa:** Họ hàng của RSI nhưng đối xứng hơn (dao động từ -100 đến +100).

### RVI (Relative Vigor Index)
*   **Công thức:** Dựa trên độ lệch chuẩn của giá đóng/mở và làm mịn theo chu kỳ.
*   **Ý nghĩa:** Nhận diện momentum theo hướng “mở cửa/đóng cửa”.

---

## 3️⃣ Biến động (Volatility)

### ATR (Average True Range)
*   **Công thức:** 
    *   TR = max(H - L, |H - C_prev|, |L - C_prev|)
    *   ATR = SMA(TR, n)
*   **Ý nghĩa:** Đo độ dao động thực của giá. ATR là công cụ cực hữu ích để đặt stop loss theo biến động thực tế.
*   **Ví dụ:** H=105, L=98, C_prev=100 → TR = 7.

### Bollinger Bands
*   **Công thức:** 
    *   Mid = SMA_20
    *   Upper = Mid + 2σ
    *   Lower = Mid - 2σ
*   **Ý nghĩa:** Dải giá theo độ lệch chuẩn.
*   **Ví dụ:** Mid=100, σ=3 → Dải trên 106 và Dải dưới 94.

### Bollinger %B
*   **Công thức:** %B = (Price - Lower) / (Upper - Lower)
*   **Ý nghĩa:** Giá đang ở đâu trong dải Bollinger.

### Bollinger Bandwidth
*   **Công thức:** BBW = [(Upper - Lower) / Mid] × 100%
*   **Ý nghĩa:** Đo độ co giãn (mở rộng/thu hẹp) của dải.

### Keltner Channel
*   **Công thức:** Upper = EMA + m × ATR  |  Lower = EMA - m × ATR
*   **Ý nghĩa:** Dải giá theo ATR thay vì Độ lệch chuẩn (σ).

### STARC Bands
*   **Công thức:** Dải giá quanh SMA/EMA cộng trừ ATR.
*   **Ý nghĩa:** Hỗ trợ xác định vùng biến động.

### Historical Volatility (Biến động lịch sử)
*   **Công thức:** σ_HV = StdDev(ln(P_t / P_t-1)) × √N
*   **Ý nghĩa:** Đo lường độ biến động lịch sử trong một chu kỳ thời gian.

### Standard Deviation (Độ lệch chuẩn)
*   **Công thức:** σ = √[ ∑(P_i - P_avg)² / n ]
*   **Ý nghĩa:** Độ phân tán giá quanh mức trung bình.

### Ulcer Index
*   **Công thức:** Dựa trên drawdown phần trăm bình phương rồi lấy căn trung bình.
*   **Ý nghĩa:** Đo “độ khó chịu” của xu hướng giảm.

### Choppiness Index
*   **Công thức:** CHOP = 100 × [ log10(∑TR / (HH - LL)) / log10(n) ]
*   **Ý nghĩa:** Đo thị trường đang đi ngang (choppy) hay có xu hướng rõ ràng.

---

## 4️⃣ Xu hướng (Trend)

### ADX (Average Directional Index)
*   **Công thức:** Từ +DI và -DI, rồi tính DX và trung bình ADX.
*   **Ý nghĩa:** Đo sức mạnh xu hướng, không cho biết hướng. Thường được dùng cùng DI để biết trend đang mạnh hay yếu.

### +DM / -DM
*   **Công thức:** 
    *   +DM = H_t - H_t-1 (nếu vượt trội hơn biến động giảm)
    *   -DM = L_t-1 - L_t (nếu vượt trội hơn biến động tăng)
*   **Ý nghĩa:** Thành phần cốt lõi của hệ thống DMI.

### Parabolic SAR
*   **Công thức:** SAR_t = SAR_t-1 + AF × (EP - SAR_t-1)
*   **Ý nghĩa:** Đặt Trailing stop theo xu hướng hiện tại.

### Ichimoku Cloud
*   **Công thức:**
    *   **Tenkan** = (9H + 9L) / 2
    *   **Kijun** = (26H + 26L) / 2
    *   **Span A** = (Tenkan + Kijun) / 2
    *   **Span B** = (52H + 52L) / 2
    *   **Chikou** = Giá đóng cửa lùi 26 phiên.
*   **Ý nghĩa:** Một hệ thống toàn diện nhìn xu hướng, động lượng và vùng hỗ trợ/kháng cự cùng lúc.

### Supertrend
*   **Công thức:** Upper/Lower band dựa trên ATR, rồi đổi trạng thái theo giá đóng cửa.
*   **Ý nghĩa:** Bám theo trend một cách trực quan trên biểu đồ.

### Aroon
*   **Công thức:** Aroon Up/Down đo số phiên kể từ đỉnh/đáy cao nhất/thấp nhất gần nhất.
*   **Ý nghĩa:** Phát hiện xu hướng mới hình thành.

### Vortex
*   **Công thức:** Dựa trên khoảng cách giữa high/low của phiên hiện tại với phiên trước.
*   **Ý nghĩa:** Nhận diện thời điểm đảo chiều xu hướng (Trend Reversal).

### Alligator
*   **Công thức:** Ba đường trung bình làm mịn khác chu kỳ (Hàm, Răng, Môi).
*   **Ý nghĩa:** Nhận diện giai đoạn “ngủ” và “thức” của thị trường.

### Schaff Trend Cycle
*   **Công thức:** Kết hợp MACD và chu kỳ Stochastic.
*   **Ý nghĩa:** Bắt nhịp xu hướng sớm hơn và mượt hơn MACD đơn lẻ.

### Pring KST (Know Sure Thing)
*   **Công thức:** Dựa trên nhiều ROC làm mịn với chu kỳ khác nhau.
*   **Ý nghĩa:** Xác nhận xu hướng trung và dài hạn.

---

## 5️⃣ Khối lượng (Volume)

### OBV (On-Balance Volume)
*   **Công thức:** 
    *   Nếu giá tăng: OBV_t = OBV_t-1 + Volume_t
    *   Nếu giá giảm: Trừ đi Volume.
*   **Ý nghĩa:** Dòng tiền đi theo hướng giá.

### MFI (Money Flow Index)
*   **Công thức:** Dựa trên Typical Price và Money Flow.
*   **Ý nghĩa:** RSI nhưng có tính thêm trọng số volume. Thường dùng để xác nhận dòng tiền.

### ADL (Accumulation/Distribution Line)
*   **Công thức:** 
    *   Multiplier = [(Close - Low) - (High - Close)] / (High - Low)
    *   ADL_t = ADL_t-1 + Multiplier × Volume
*   **Ý nghĩa:** Đo lường quá trình tích lũy (mua gom) / phân phối (bán ra).

### CMF (Chaikin Money Flow)
*   **Công thức:** CMF = (∑ MoneyFlowVolume) / (∑ Volume)
*   **Ý nghĩa:** Đo áp lực mua/bán tích lũy.

### PVT (Price Volume Trend)
*   **Công thức:** PVT_t = PVT_t-1 + [(Close_t - Close_t-1) / Close_t-1] × Volume_t
*   **Ý nghĩa:** Volume được điều chỉnh theo % thay đổi giá.

### NVI / PVI (Negative / Positive Volume Index)
*   **Công thức:** NVI dùng ngày volume giảm, PVI dùng ngày volume tăng.
*   **Ý nghĩa:** Phân biệt dấu vết dòng tiền thông minh (Smart Money) và đám đông.

### Volume Oscillator
*   **Công thức:** [(EMA_short(Vol) - EMA_long(Vol)) / EMA_long(Vol)] × 100
*   **Ý nghĩa:** Cho biết khối lượng đang có xu hướng tăng hay giảm.

### Klinger Oscillator
*   **Công thức:** Kết hợp volume flow và EMA nhanh/chậm.
*   **Ý nghĩa:** Theo dõi xu hướng dòng tiền dài hạn.

### Elder Force Index
*   **Công thức:** EFI = (Close_t - Close_t-1) × Volume_t
*   **Ý nghĩa:** Đo sức mạnh (lực đẩy) của phe mua/phe bán kết hợp giá và volume.

### Twiggs Money Flow
*   **Công thức:** Biến thể đo tích lũy/phân phối với Smoothing.
*   **Ý nghĩa:** Nhận diện dòng tiền ra vào chân thực hơn.

---

## 6️⃣ Kênh giá và Mức hỗ trợ/kháng cự

### Pivot Point (Điểm xoay trục)
*   **Công thức:** P = (H + L + C) / 3. Các mức R1, R2, R3 (Kháng cự) và S1, S2, S3 (Hỗ trợ) tính từ P.
*   **Ý nghĩa:** Mức xoay quanh phiên trước. Rất phổ biến trong giao dịch trong ngày (Intraday/Phái sinh).

### Fibonacci Retracement
*   **Công thức:** Mức = High - (High - Low) × Tỷ_lệ
*   **Ý nghĩa:** Vùng giá hồi quy thường gặp. Ví dụ: 61.8%, 50%, 38.2%.

### Fibonacci Extension
*   **Công thức:** Dùng để ước lượng mục tiêu sau breakout.
*   **Ý nghĩa:** Đo vùng giá mở rộng để chốt lời.

### Donchian Channel
*   **Công thức:** Upper = Highest High n phiên, Lower = Lowest Low n phiên.
*   **Ý nghĩa:** Dùng để theo dõi Breakout đỉnh/đáy.

### Darvas Box (Hộp Darvas)
*   **Công thức:** Dựa trên vùng tích lũy và breakout.
*   **Ý nghĩa:** Lọc cổ phiếu mạnh đang trong xu hướng lên.

### Support / Resistance
*   **Ý nghĩa:** Xác định từ đáy/đỉnh cũ, đường MA, Pivot, Fibo để tìm vùng phản ứng giá.

### Gann Fan
*   **Công thức:** Các đường góc xuất phát từ một điểm gốc (đỉnh/đáy quan trọng).
*   **Ý nghĩa:** Hỗ trợ xác định nhịp xu hướng và kháng cự chéo.

### ZigZag
*   **Công thức:** Lọc dao động nhỏ theo ngưỡng %.
*   **Ý nghĩa:** Nhìn rõ cấu trúc sóng chính mà không bị nhiễu.

---

## 7️⃣ Thống kê (Statistics)

### Linear Regression Slope
*   **Ý nghĩa:** Độ dốc của đường hồi quy tuyến tính → đo tốc độ xu hướng.

### Linear Regression Forecast
*   **Ý nghĩa:** Dự báo giá theo đường hồi quy → ước lượng nhịp giá tiếp theo.

### Linear Regression Intercept
*   **Ý nghĩa:** Giao điểm với trục tung → thành phần nền của hồi quy.

### Correlation Coefficient (r)
*   **Ý nghĩa:** r đo mức tương quan giữa giá và biến khác → kiểm tra đồng biến/nghịch biến.

### R-Squared (R²)
*   **Ý nghĩa:** Độ phù hợp của mô hình hồi quy → cho biết mô hình giải thích được bao nhiêu % biến động giá.

### TSF (Time Series Forecast)
*   **Ý nghĩa:** Dự báo chuỗi thời gian từ mô hình hồi quy → dùng cho dự báo ngắn hạn.

---

## 8️⃣ Quản trị rủi ro

### Position Sizing (Tính khối lượng lệnh)
*   **Công thức:** Số lượng cổ phiếu = (Vốn × % rủi ro) / (Entry - Stop)
*   **Ý nghĩa:** Kiểm soát mức lỗ tối đa cho mỗi lệnh.

### Risk / Reward Ratio (Tỷ lệ R/R)
*   **Công thức:** R/R = (Target - Entry) / (Entry - Stop)
*   **Ý nghĩa:** Chọn lệnh có kỳ vọng tốt (thường từ 1:2 trở lên).

### Expected Value (Kỳ vọng toán học)
*   **Công thức:** EV = (WinRate × AvgWin) - (LossRate × AvgLoss)
*   **Ý nghĩa:** Lợi thế thống kê của hệ thống giao dịch.

### Max Drawdown
*   **Công thức:** [(Peak - Trough) / Peak] × 100%
*   **Ý nghĩa:** Mức sụt giảm lớn nhất từ đỉnh vốn.

### Sharpe Ratio
*   **Công thức:** (R_p - R_f) / σ_p
*   **Ý nghĩa:** Lợi nhuận điều chỉnh theo mức rủi ro gánh chịu.

### ATR Stop Loss
*   **Công thức:** Stop = Entry ± (k × ATR)
*   **Ý nghĩa:** Đặt Stop loss linh hoạt theo biên độ dao động thực tế của mã cổ phiếu.

### Trailing Stop ATR
*   **Công thức:** Dời stop loss tịnh tiến lên (lệnh mua) theo ATR khi giá đi đúng hướng.
*   **Ý nghĩa:** Khóa lợi nhuận an toàn để không bị quét râu nến.

---

## 🔍 Mở rộng 100+ mục tra cứu nhanh

Để tối ưu tra cứu, dưới đây là các biến thể và chu kỳ mặc định phổ biến nhất:

*   **SMA:** 5, 10, 20, 50, 100, 200
*   **EMA:** 5, 10, 20, 50, 100, 200
*   **RSI:** 2, 7, 14, 21
*   **ATR:** 7, 14, 21
*   **MACD:** 5-35-5, 12-26-9
*   **Stochastic:** 5-3-3, 14-3-3
*   **Bollinger Bands:** 20-2, 50-2
*   **Keltner Channel:** 20-2 ATR
*   **Supertrend:** 10-3, 14-2
*   **Ichimoku:** 9-26-52
*   **Pivot:** Classic, Fibonacci, Camarilla
*   **Donchian:** 20, 55
*   **OBV:** trendline
*   **MFI:** 14
*   **ADX:** 14
*   **Aroon:** 25
*   **Vortex:** 14
*   **CCI:** 20
*   **ROC:** 12, 25
*   **TRIX:** 15
*   **CMO:** 14
*   **Mô hình/Phân kỳ:** RSI Divergence, MACD Divergence, Volume Divergence, Price Action Breakout.
*   **Hành động giá:** Gap Up, Gap Down, Higher High, Lower Low, Higher Low, Lower High.

---

## ⚡ Cách đọc nhanh & Tư duy phân tích

> [!IMPORTANT]
> 1. **SMA/EMA** → Cho biết xu hướng nền trung/dài hạn.
> 2. **RSI / Stochastic / MACD** → Cho biết động lượng (Quá mua/Quá bán, Cắt lên/xuống).
> 3. **ATR / Bollinger / Keltner** → Cho biết biên độ biến động (Nén hay mở rộng).
> 4. **OBV / MFI / CMF / ADL** → Xác nhận dòng tiền thực tế có hậu thuẫn cho giá hay không.
> 5. **ADX / Ichimoku / Supertrend** → Cho biết xu hướng hiện tại mạnh hay yếu.
> 6. **Pivot / Fibo / Donchian** → Giúp xác định vùng giá quan trọng để đặt Lệnh (Entry) và Chốt lời (Target).
> 7. **Lưu ý đặc biệt với Ichimoku:** Nên được đọc như một bộ gồm các đường và vùng mây, không phải một đường đơn lẻ; Cloud được tạo bởi Senkou Span A và B, và chính phần mây này cho biết vùng hỗ trợ/kháng cự cùng hướng xu hướng (Mây dày = cản mạnh, mây mỏng = dễ xuyên thủng).

---

### 📂 Gợi ý bố cục xuất PDF cuối cùng (Nếu in ấn)
*   **Trang 1:** Bìa
*   **Trang 2:** Mục lục
*   **Trang 3–5:** Công thức nền tảng
*   **Trang 6–10:** Xu hướng và động lượng
*   **Trang 11–14:** Biến động và khối lượng
*   **Trang 15–18:** Kênh giá, Ichimoku, thống kê
*   **Trang 19:** Quản trị rủi ro
*   **Trang 20:** Bảng tra cứu nhanh 100+ mục
