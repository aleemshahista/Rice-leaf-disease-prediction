# 🌾 RiceGuard AI — Rice Leaf Disease Prediction System

AI-powered full-stack web application that helps farmers and agronomists identify rice leaf diseases instantly using deep learning. Upload a rice leaf photo and get disease classification, confidence scores, Grad-CAM heatmaps, and treatment recommendations.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   React +   │────▶│   FastAPI     │────▶│  PostgreSQL  │
│   Vite UI   │     │   Backend     │     │   Database   │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │ EfficientNet │
                    │   B3 Model   │
                    └──────────────┘
```

## ✨ Features

- 🌾 AI-powered rice leaf disease detection
- 🎯 Confidence score prediction
- 🔥 Grad-CAM visualization for model explainability
- 💊 Disease treatment recommendations
- 📜 Prediction history tracking
- 🔒 Secure JWT-based user authentication
- 📤 Image upload and analysis
- 📊 Interactive dashboard with prediction insights

**Tech Stack:**
- **Frontend:** React 18, Vite, Tailwind CSS v3, Framer Motion, Recharts
- **Backend:** FastAPI, SQLAlchemy, JWT Auth, SlowAPI rate limiting
- **ML Model:** EfficientNet-B3 (fine-tuned), Grad-CAM visualizations
- **Infra:** Docker Compose, Nginx, PostgreSQL 15, Redis 7, GitHub Actions CI/CD

## Disease Classes (8)

| # | Disease | Severity |
|---|---------|----------|
| 0 | Healthy | None |
| 1 | Blast (Magnaporthe oryzae) | High |
| 2 | Brown Spot (Bipolaris oryzae) | Medium |
| 3 | Sheath Blight (Rhizoctonia solani) | High |
| 4 | Bacterial Leaf Blight (Xanthomonas oryzae) | High |
| 5 | Tungro (rice tungro virus) | High |
| 6 | False Smut (Ustilaginoidea virens) | Medium |
| 7 | Narrow Brown Leaf Spot | Low |

## Quick Start

### Prerequisites
- Docker & Docker Compose
- (Optional) NVIDIA GPU + CUDA for model training

### 1. Clone & Run

```bash
git clone <your-repo-url>
cd rice-disease-prediction

# Start all services
docker-compose up --build
```

Services:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Nginx Proxy:** http://localhost:80

### 2. Run Without Docker (Development)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Start server (requires PostgreSQL running)
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Dataset Setup & Model Training

### 1. Download Datasets

Download from Kaggle and organize into a single directory:

- **Primary:** [Rice Leaf Disease](https://www.kaggle.com/datasets/shaikusmanshafi/riceleafdisease)
- **Supplementary:** [Rice Disease Image Dataset](https://www.kaggle.com/datasets/minakhisrivedi/rice-disease-image-dataset)

```
data/rice_disease/
├── Healthy/
├── Blast/
├── BrownSpot/
├── SheathBlight/
├── BacterialLeafBlight/
├── Tungro/
├── FalseSmut/
└── NarrowBrownLeafSpot/
```

### 2. Train the Model

```bash
cd backend
python -m ml.train \
  --data_dir ../data/rice_disease \
  --output_dir ./ml/model \
  --epochs1 10 \
  --epochs2 20 \
  --batch_size 32
```

Training uses a two-phase strategy:
1. **Phase 1:** Freeze backbone, train classifier head (10 epochs, lr=1e-3)
2. **Phase 2:** Unfreeze last 2 blocks, fine-tune (20 epochs, lr=1e-4, CosineAnnealing)

### 3. Evaluate

```bash
python -m ml.evaluate --data_dir ../data/rice_disease --model_path ./ml/model/efficientnet_rice.pth
```

### Demo Mode

If no trained model file exists, the app runs in **demo mode** with simulated predictions — useful for UI testing.

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login, get JWT token | No |
| GET | `/api/auth/me` | Get current user profile | Yes |
| POST | `/api/predict` | Upload image, get prediction | Yes |
| GET | `/api/history` | Paginated prediction history | Yes |
| GET | `/api/history/{id}` | Single prediction detail | Yes |
| DELETE | `/api/history/{id}` | Delete a prediction | Yes |
| GET | `/api/health` | Health check + model status | No |

Full interactive API docs at: **http://localhost:8000/docs**

## Running Tests

```bash
# Backend tests
cd backend
pytest -v

# Frontend tests
cd frontend
npx vitest run
```

## Environment Variables

See `backend/.env.example` for all backend configuration options.

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://riceuser:ricepass123@db:5432/rice_disease` |
| `SECRET_KEY` | JWT signing secret | (change in production!) |
| `MODEL_PATH` | Path to trained model weights | `./ml/model/efficientnet_rice.pth` |
| `STORAGE_TYPE` | `local` or `s3` | `local` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |

## Production Deployment

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## License

MIT
