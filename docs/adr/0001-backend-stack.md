# 0001 — Stack backend: FastAPI, Python 3.12, uv

- Status: accepted
- Tanggal: 2026-11-14

## Konteks
Tim memakai Python untuk backend dan AI. Standar ECC proyek (`.agents/rules/python-fastapi.md`)
mengatur struktur FastAPI. Image Docker memakai `python:3.12-slim`.

## Keputusan
- FastAPI dengan `create_app()`, satu paket per fitur di `app/features/` (router tipis, schemas, service).
- Python 3.12 dikunci (`requires-python >=3.12,<3.13`, `.python-version`).
- Dependency dikelola dengan uv; `uv.lock` di-commit.
- Dependency opsional dipisah per extra: `db`, `cache`, `worker`, `ml`.
- PostGIS dan Redis tersedia di docker compose, tetapi baru dipakai bila sebuah modul membutuhkannya.

## Alternatif yang dipertimbangkan
- pip + requirements.txt: tanpa lockfile lintas platform yang deterministik.
- Satu set dependency besar: image lebih berat untuk modul yang tidak butuh ML/DB.

## Konsekuensi
- Semua anggota perlu Python 3.12 dan uv (atau pip dengan `pip install -e ".[dev]"`).
- Menambah dependency wajib lewat `uv add` agar `uv.lock` ikut berubah.
