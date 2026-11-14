# backend-nasa — Field Shift API (FastAPI)

Kerangka backend dan AI. Belum ada fitur; baru `/health` dan router `/api/v1` kosong.

## Struktur

```
app/
  main.py          create_app(): CORS dari env, error handler, router
  core/            config (env), logging (text/JSON), errors, schemas (envelope), rate_limit
  api/router.py    router /api/v1 — daftarkan router fitur di sini
  features/        satu paket per fitur: router.py (tipis), schemas.py, service.py
    health/        GET /health
  ai/              modul AI/model murni (tanpa import FastAPI)
  data/            repository data (datasets/, nanti PostGIS)
  workers/         job latar belakang (opsional)
configs/           config eksperimen (seed, parameter)
datasets/          data olahan (tidak masuk Git) + manifest.yaml
models/            artefak model (tidak masuk Git) + registry.yaml
scripts/           export_openapi.py, nanti pipeline data
tests/unit, tests/integration
```

## Jalankan

```bash
cd backend-nasa
# Python 3.12 + uv (https://docs.astral.sh/uv/)
uv sync --extra dev                  # tambah extra sesuai modul: --extra db --extra ml ...
cp .env.example .env
uv run uvicorn app.main:app --reload # http://localhost:8000/docs
uv run pytest                        # coverage minimal 80%
uv run ruff check . && uv run black --check . && uv run mypy app
uv run python -m scripts.export_openapi   # perbarui ../contracts/openapi.json
```

Tanpa uv: `python -m venv .venv`, aktifkan, lalu `pip install -e ".[dev]"`.

Docker (dari root repo): salin `../.env.example` ke `../.env`, isi `POSTGRES_PASSWORD`, lalu
`docker compose up -d --build`. Extra opsional di image: `--build-arg EXTRAS=db,cache`.

## Extra dependency

| Extra | Isi | Untuk |
| --- | --- | --- |
| `dev` | pytest, ruff, black, mypy, bandit, pip-audit | semua anggota |
| `db` | SQLAlchemy async, asyncpg, GeoAlchemy2, Alembic | modul yang memakai PostGIS |
| `cache` | redis | cache / antrean |
| `worker` | arq | job komputasi panjang |
| `ml` | numpy, pandas, scikit-learn, xarray | modul AI |

Tambah dependency: `uv add <paket>` (atau `--optional <extra>`), lalu commit `uv.lock`.

## Kontrak API

Setiap mengubah endpoint atau schema, jalankan `export_openapi` dan commit `contracts/openapi.json`.
Frontend membuat tipe TypeScript darinya dengan `npm run gen:api`. CI gagal jika kontrak tidak diperbarui.

## Data dan model

File data dan model tidak masuk Git. Catat setiap dataset di `datasets/manifest.yaml`, setiap model
di `models/registry.yaml`, dan simpan salinan `configs/experiment.example.yaml` per eksperimen.

## Konvensi (ECC, lihat ../AGENTS.md)

- Endpoint I/O memakai `async def`; komputasi berat dijalankan di threadpool.
- Router tipis, logika di `service.py` / `app/ai`, schema request dan response terpisah.
- Tanpa `print()`, pakai `logging`. Rahasia hanya dari env.
- Format response wajib `ApiResponse` lewat `ok()` (lihat `../docs/adr/0002-response-envelope.md`).
- Urutan import: ECC menyebut isort; di sini dijalankan oleh ruff (aturan `I`, kompatibel dengan
  profil black), jadi tidak perlu memasang isort terpisah.
- Pre-commit: dari root repo jalankan `pre-commit install` sekali.
- Test dulu (TDD), coverage ≥ 80%.
