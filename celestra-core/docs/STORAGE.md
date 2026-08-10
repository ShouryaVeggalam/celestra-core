# Storage — Celestra Core (Phase 5)

Object storage for uploads across all Celestra apps.

## Backends

| Backend | When |
|---|---|
| `local` | Default — files under `CELESTRA_STORAGE_LOCAL_PATH` |
| `memory` | Tests |
| `s3` | When endpoint + access/secret keys set (MinIO/gateway compatible) |

## Usage

```python
from storage import StorageService

info = await storage.upload("reports/a.pdf", data, content_type="application/pdf")
obj = await storage.download("reports/a.pdf")
url = await storage.signed_url("reports/a.pdf")
```

## HTTP (`/api/v1/storage`) — auth required

| Method | Path |
|---|---|
| POST | `/upload` |
| GET | `/objects/{key}` |
| DELETE | `/objects/{key}` |
| GET | `/objects/{key}/url` |
| GET | `/objects?prefix=` |
