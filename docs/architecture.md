# Arsitektur

> Status: draft.

## Konteks sistem
<!-- Siapa/apa yang berinteraksi dengan sistem. -->

## Komponen

| Komponen | Folder | Tanggung jawab | Pemilik |
| --- | --- | --- | --- |
| Backend API | `backend-nasa/app` | | |
| Modul AI | `backend-nasa/app/ai` | | |
| Akses data | `backend-nasa/app/data` | | |
| Frontend | `frontend-nasa` | | |
| Database | PostGIS (docker compose) | | |
| Cache/antrean | Redis (docker compose) | | |

## Aliran data
<!-- Dari sumber data mentah sampai tampilan di frontend. -->

## Kontrak antar komponen
- API: `contracts/openapi.json` (format response: `docs/adr/0002-response-envelope.md`)

## Keputusan terkait
Lihat `docs/adr/`.
