# Hướng dẫn Deploy Docker trên Linux Server

## 1. Yêu cầu

- Linux server (Ubuntu 20.04+)
- Docker & Docker Compose

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

## 2. Cấu hình Telegram (bắt buộc)

Tạo file `.env` trong thư mục dự án:

```bash
cat > .env << 'EOF'
TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
EOF
```

> Bỏ trống nếu không dùng — app vẫn chạy nhưng không gửi tin nhắn.

## 3. Deploy — 1 lệnh duy nhất

```bash
docker compose up -d
```

Kiểm tra:

```bash
curl http://localhost:8000/api/health
```

## 4. Cronjob

**Không cần cronjob hệ thống.** Pipeline tự động chạy lúc 2:00 AM mỗi ngày nhờ APScheduler tích hợp trong app.

Để thay đổi giờ chạy, sửa biến trong `.env`:

```bash
echo "PIPELINE_HOUR=6" >> .env
echo "PIPELINE_MINUTE=30" >> .env
docker compose down && docker compose up -d
```

## 5. Database

DB được lưu trong Docker volume (`stock_data`), **hoàn toàn tách biệt khỏi source code**. Không có file `.db` nào ở thư mục dự án.

```bash
# Backup
docker run --rm -v stock_data:/data -v $(pwd):/backup alpine tar czf /backup/stock_data_backup.tar.gz -C /data .

# Restore
docker run --rm -v stock_data:/data -v $(pwd):/backup alpine tar xzf /backup/stock_data_backup.tar.gz -C /data
```

Hoặc backup bằng cp:

```bash
docker compose exec stock-analysis cp /app/data/stock_data.db /app/data/backup_$(date +%Y%m%d).db
```

## 6. Các lệnh quản lý

```bash
# Logs
docker compose logs -f --tail 100

# Restart
docker compose restart

# Dừng
docker compose down

# Cập nhật code mới
git pull
docker compose build
docker compose up -d

# Xoá toàn bộ (mất DB!)
docker compose down -v
```

## 7. API

```bash
# Health
curl http://localhost:8000/api/health

# Danh sách predictions
curl http://localhost:8000/api/predictions

# Tra cứu 1 mã
curl http://localhost:8000/api/predictions/ACB

# Chạy pipeline thủ công
curl -X POST http://localhost:8000/api/run-pipeline
```
