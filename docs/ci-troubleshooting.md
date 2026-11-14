# CI troubleshooting

Kegagalan yang paling mungkin di `backend-ci` dan `frontend-ci`, dan cara memperbaikinya lokal
sebelum push. Semua perintah backend dijalankan dari `backend-nasa/`.

| Langkah gagal | Penyebab umum | Perbaikan |
| --- | --- | --- |
| `uv sync --frozen` | `pyproject.toml` diubah tanpa memperbarui lockfile | `uv lock`, commit `uv.lock` |
| `ruff check` | Import tidak urut, aturan keamanan `S`, baris > 100 | `uv run ruff check --fix .` lalu perbaiki sisanya |
| `black --check` | Format berbeda | `uv run black .` |
| `mypy app` | Fungsi tanpa anotasi tipe (mode strict) | Tambahkan tipe parameter dan return |
| `bandit` | Pola berisiko (mis. `subprocess` dengan shell, `assert` di kode app) | Ubah kodenya; `# nosec` hanya dengan alasan tertulis |
| Dependency audit | Ada CVE di dependency | Naikkan versi paket (`uv lock --upgrade-package <nama>`) |
| `pytest` coverage < 80% | Kode baru tanpa test | Tambahkan test (TDD: test dulu) |
| "API contract is up to date" | Endpoint/schema berubah tapi `contracts/openapi.json` belum diperbarui | `uv run python -m scripts.export_openapi`, commit hasilnya |
| `npm ci` (frontend) | `package-lock.json` tidak sinkron dengan `package.json` | `npm install` lokal, commit lockfile |
| `npm run gen:api` | `contracts/openapi.json` rusak atau tidak ada | Export ulang dari backend |
| `npm run lint` / `build` | Error ESLint atau TypeScript | `npm run lint`, `npx tsc -b` lokal |
| Upload SARIF | Code scanning tidak aktif untuk repo privat tanpa GitHub Advanced Security | Langkah ini `continue-on-error`; laporan tetap tersimpan sebagai artefak |

Jalankan semua cek backend sekaligus sebelum push:

```bash
uv run ruff check . && uv run black --check . && uv run mypy app \
  && uv run bandit -q -c pyproject.toml -r app && uv run pytest
```

## Bukti keamanan dan test (artefak CI)

Setiap run menyimpan artefak `backend-evidence-<sha>` dan `frontend-evidence-<sha>` selama 30 hari
(tab **Actions** → run → **Artifacts**), juga saat run gagal:

| File | Isi |
| --- | --- |
| `bandit.sarif` | Hasil analisis statis Bandit (juga dikirim ke Code Scanning bila tersedia) |
| `pip-audit.json` | Audit kerentanan dependency Python dari `uv.lock` |
| `requirements.lock.txt` | Daftar dependency terkunci yang diaudit |
| `sbom.cdx.json` | SBOM CycloneDX (backend dan frontend) |
| `coverage.xml`, `junit.xml` | Coverage dan hasil test backend |
| `npm-audit.json` | Audit dependency frontend (gagal hanya untuk high/critical) |

## Keamanan workflow

- Token CI hanya `contents: read`; job backend menambah `security-events: write` khusus untuk upload SARIF.
- Semua action di-pin ke commit SHA (tag ada di komentar). Saat memperbarui, ganti SHA dan komentarnya
  bersamaan, ambil SHA dari halaman rilis resmi action tersebut.
- `persist-credentials: false` pada checkout, jadi token tidak tertinggal di `.git/config` runner.
