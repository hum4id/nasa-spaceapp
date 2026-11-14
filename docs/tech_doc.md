# Dokumentasi teknis

## Menjalankan lokal
- Backend: lihat `backend-nasa/README.md`
- Frontend: lihat `frontend-nasa/README.md`
- Semua service: salin `.env.example` ke `.env`, isi `POSTGRES_PASSWORD`, lalu `docker compose up -d --build`

## Konfigurasi (env)
- Backend: `backend-nasa/.env.example`
- Frontend: `frontend-nasa/.env.example`
- Docker compose: `.env.example` di root

## Konvensi
- Standar kode: `AGENTS.md` dan `.agents/rules/`
- Format response API: `docs/adr/0002-response-envelope.md`
- Commit: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`, `ci:`, ...)
- Pre-commit: `pre-commit install` sekali per clone

## Deploy
<!-- Isi saat target deploy diputuskan. -->
