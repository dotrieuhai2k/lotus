# [RUNBOOK] Tên sự cố (Ví dụ: High Latency API)

| Mức độ | Trigger (Cảnh báo) | Người phụ trách |
| :--- | :--- | :--- |
| **P1 - Critical** | Alert `High_Latency > 5s` | Team Backend / SRE |

## 1. Triệu chứng
Làm sao biết lỗi này đang xảy ra?
* Alert bắn về Slack channel `#ops-alerts`.
* User báo lỗi timeout.

## 2. Các bước xử lý (Mitigation Steps)

### Bước 1: Kiểm tra Logs
Chạy lệnh sau để xem log lỗi:
```bash
kubectl logs -l app=lotus-worker --tail=100
```

### Bước 2: Khắc phục tạm thời
Nếu do Worker bị treo, hãy restart pod:
```bash
kubectl rollout restart deployment/lotus-worker
```

### Bước 3: Leo thang (Escalation)
Nếu sau 15 phút không fix được, gọi ngay cho:
* **Leader:** [SĐT]
* **DBA:** [SĐT]

## 3. Hậu kiểm (Post-Mortem)
* Check lại biểu đồ latency đã giảm chưa?
* Thử tạo 1 giao dịch test.