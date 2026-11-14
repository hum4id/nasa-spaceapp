# 0002 — Format response API seragam (envelope)

- Status: accepted
- Tanggal: 2026-11-14

## Konteks
ECC `common-patterns.md` mewajibkan satu bentuk response untuk semua endpoint. Frontend
membuat tipe TypeScript dari `contracts/openapi.json`, sehingga bentuk response harus stabil.

## Keputusan
Semua response, sukses maupun gagal, memakai `ApiResponse` (`backend-nasa/app/core/schemas.py`):

```json
{ "success": true,  "data": {}, "error": null, "meta": null }
{ "success": false, "data": null, "error": { "code": "not_found", "message": "...", "details": null }, "meta": null }
```

- Endpoint sukses: `return ok(data)`, dengan `response_model=ApiResponse[Schema]`.
- Error: raise `DomainError` atau turunannya; handler di `app/core/errors.py` mengubahnya ke envelope.
- 404, 405, 422 (validasi), 429 (rate limit), dan 500 juga memakai envelope; 500 tidak pernah
  menampilkan detail internal.
- `error.code` adalah string stabil yang boleh dipakai frontend untuk logika; `message` untuk ditampilkan.
- `meta` dipakai untuk paginasi (`total`, `page`, `limit`).

## Konsekuensi
- Frontend cukup memeriksa `success` dan `error.code`.
- Endpoint baru wajib memakai `ok()` dan `response_model`; review menolak bentuk lain.
