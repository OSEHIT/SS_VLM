#  SMART SHELF - Assistant d'Inventaire IA (Backend)

> API **FastAPI** propulsant l'application mobile Smart Shelf. Elle orchestre la détection de produits via **codes-barres/QR**, l'intégration **OpenFoodFacts**, et l'analyse visuelle par un modèle **VLM (Qwen2-VL)** pour les produits en vrac.

---

##  Fonctionnalités de l'API

-  **Décodage barcode / QR Code** — Extraction de l'EAN via `pyzbar`.
-  **Intégration OpenFoodFacts** — Récupération automatique des infos produit (nom, marque, image).
-  **Analyse VLM (Mode Vrac)** — Comptage et estimation DLC pour les produits sans code-barres via **Qwen2-VL-2B-Instruct**.
-  **CRUD Inventaire** — Gestion complète des produits via MongoDB.
-  **Pipeline RL Feedback** — Sauvegarde des prédictions VLM et des corrections utilisateur pour l'entraînement futur.
-  **Export** — Export des données d'inventaire.
-  **Health Check** — Endpoint `/health` indiquant l'état du VLM et de la version.

---

## 🛠️ Prérequis

| Outil | Version minimale | Lien |
|---|---|---|
| Python | 3.9+ | [python.org](https://www.python.org/downloads/) |
| MongoDB | 6.0+ | [mongodb.com](https://www.mongodb.com/try/download/community) |
| pip | Inclus avec Python | — |



---

##  Installation

### 1. Créer un environnement virtuel

```bash
python -m venv .venv

# Activer l'environnement :
# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

*Ou, si vous utilisez `pyproject.toml` :*

```bash
pip install -e .
```

Pour les outils de développement (tests, linter) :

```bash
pip install -e ".[dev]"
```

---

##  Configuration des Variables d'Environnement

Copiez le fichier d'exemple et renseignez vos valeurs :

```bash
cp .env.example .env
```

Ouvrez `.env` et configurez les variables suivantes :

```ini
# === Smart Shelf V2 — Environment Variables ===

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=smartshelf_rl

# VLM Model (téléchargé depuis Hugging Face)
VLM_MODEL_ID=Qwen/Qwen2-VL-2B-Instruct
VLM_DEVICE=cpu        # Utiliser "cuda" si vous avez un GPU NVIDIA

# Serveur
HOST=0.0.0.0
PORT=8000
DEBUG=true

# OpenFoodFacts
OFF_BASE_URL=https://world.openfoodfacts.org/api/v2
OFF_TIMEOUT=10
```

> [!IMPORTANT]
> Mettez `VLM_DEVICE=cuda` si vous disposez d'un GPU compatible CUDA pour des performances optimales. En mode `cpu`, l'inférence VLM sera plus lente.

---

##  Lancement du Serveur

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

##  Endpoints Principaux

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | Vérifie l'état du serveur et du VLM |
| `POST` | `/api/v1/scan` | Scan d'image(s) — barcode ou vrac (VLM) |
| `GET` | `/api/v1/products/` | Liste tous les produits en inventaire |
| `POST` | `/api/v1/products/` | Ajoute un produit à l'inventaire |
| `GET` | `/api/v1/products/{id}` | Récupère un produit par son ID |
| `PUT` | `/api/v1/products/{id}` | Met à jour un produit |
| `DELETE` | `/api/v1/products/{id}` | Supprime un produit |
| `POST` | `/api/v1/rl-feedback` | Soumet un feedback de correction VLM |
| `GET` | `/api/v1/export` | Exporte les données d'inventaire |

 **Documentation interactive complète :** [http://localhost:8000/docs](http://localhost:8000/docs)

---

##  Structure du Projet

```
backend/
├── app/
│   ├── main.py               #  Factory FastAPI + lifespan
│   ├── config.py             #  Paramètres via variables d'env
│   ├── routes/
│   │   ├── scan.py           #  Endpoint /scan
│   │   ├── products.py       #  CRUD inventaire
│   │   ├── rl_feedback.py    #  Feedback RL
│   │   └── export.py         #  Export données
│   ├── services/
│   │   ├── scan_orchestrator.py  #  Pipeline principal de scan
│   │   ├── vlm_service.py        #  Inférence Qwen2-VL
│   │   ├── barcode_service.py    #  Décodage pyzbar
│   │   └── off_service.py        #  OpenFoodFacts
│   ├── dependencies/
│   │   ├── vlm.py            # Conteneur singleton VLM
│   │   └── mongodb.py        # Connexion MongoDB
│   └── schemas/              # Modèles Pydantic
├── tests/                    # Tests pytest
├── .env                      # Variables d'environnement (non versionné)
├── .env.example              # Modèle de configuration
├── requirements.txt          # Dépendances Python
└── pyproject.toml            # Configuration projet & dev tools
```

---

##  Tests

```bash
pytest
```

Les tests sont situés dans le dossier `tests/` et utilisent `pytest-asyncio` pour les routes asynchrones.

---

##  Lien avec le Frontend

Ce backend est consommé par l'application mobile **Expo** du dossier `smart-shelf/`. Assurez-vous que :
1. Le serveur écoute sur `0.0.0.0` (et non `127.0.0.1`) pour être accessible depuis le réseau local.
2. L'adresse IP de cette machine est bien renseignée dans `smart-shelf/config/api.ts` côté frontend.
