# Smart Shelf V2 — Backend API

> FastAPI + Qwen2-VL-2B + OpenFoodFacts + MongoDB

## Quick Start

```bash
# 1. Installer les dépendances
cd backend
pip install -e ".[dev]"

# 2. Copier les variables d'environnement
cp .env.example .env

# 3. Lancer le serveur
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Swagger UI
# → http://localhost:8000/docs
```

## Architecture

```
app/
├── main.py              # App factory + Lifespan (VLM + MongoDB)
├── config.py            # Pydantic Settings
├── core/                # Exceptions, prompts VLM
├── schemas/             # Modèles Pydantic (ScanResponse, OFFData, RLExport)
├── routes/              # POST /scan, GET /export/rl-dataset
├── services/            # barcode, OFF, VLM, scan_orchestrator
└── dependencies/        # DI: VLM container, MongoDB client
```

## Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/v1/scan` | Scanner un produit (images multipart) |
| `GET` | `/api/v1/export/rl-dataset` | Exporter le dataset RL |
| `GET` | `/api/v1/export/rl-dataset/count` | Compter les entrées RL |
| `GET` | `/health` | Health check + état VLM |

## Tests

```bash
pytest tests/ -v
```

## Prérequis

- Python 3.11+
- MongoDB (pour le dataset RL)
- `zbar` library (pour pyzbar : `apt install libzbar0` ou `choco install zbar`)
