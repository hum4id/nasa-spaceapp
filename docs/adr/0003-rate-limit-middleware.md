# 0003 — Rate limit global dengan middleware ASGI berbasis `limits`

- Status: accepted
- Tanggal: 2026-11-14

## Konteks
ECC `common-security.md` mewajibkan rate limit di semua endpoint. Versi awal memakai middleware
slowapi. Test integrasi menunjukkan limit global **tidak pernah aktif**: FastAPI 0.162 membungkus
router yang di-include (`_IncludedRouter`), sehingga slowapi tidak menemukan endpoint dan
meloloskan semua request.

## Keputusan
`app/core/rate_limit.py`: middleware ASGI kecil di atas library `limits` (moving window,
penyimpanan in-memory), dikunci per IP klien dari scope ASGI, dengan response 429 berformat
envelope dan header `Retry-After`. Batas default dari `RATE_LIMIT_DEFAULT`.

## Konsekuensi
- Penyimpanan in-memory berlaku per proses. Jika backend dijalankan dengan beberapa worker atau
  replika, pindahkan storage ke Redis (`limits` mendukungnya) agar limit dihitung bersama.
- Di belakang reverse proxy, uvicorn harus memakai `--proxy-headers` dan `FORWARDED_ALLOW_IPS`
  berisi alamat proxy; jika tidak, semua klien terhitung sebagai satu IP.
- Limit per endpoint (mis. POST komputasi berat) ditambahkan saat endpoint itu dibuat.
