# Federated Multimodal Air Quality Prediction

This project is a web-based air quality prediction system. It combines image data and weather-related tabular data to predict the AQI category using trained multimodal models.

The system includes a Vue frontend, a FastAPI backend, and an Nginx reverse proxy. It can be started with Docker Compose.

## Features

- Select built-in sample images with predefined weather data.
- Upload a custom image and manually enter weather data.
- Choose a prediction model, such as Taiwan, India, or global model.
- Send the image and tabular data to the backend for AQI prediction.
- Display the predicted AQI level and its health description.

## Project Structure

```text
VQAweb-AQI
|-- backend
|   |-- main.py                 # FastAPI prediction API
|   |-- feature_manager.py      # Image and tabular feature extraction
|   |-- m_model.py              # CNN and tabular MLP modules
|   |-- mm_models.py            # Multimodal prediction model
|   |-- requirements.txt
|   `-- fed_multimodal_restcol  # Training and preprocessing modules
|-- frontend
|   `-- Present
|       |-- src                 # Vue frontend source code
|       |-- public              # Images and static assets
|       `-- package.json
|-- nginx
|   |-- nginx.conf
|   `-- conf.d/default.conf
|-- docker-compose.yml
`-- README.md
```

## System Architecture

```text
Browser
   |
   v
Nginx :8000
   |----------------> Frontend :8000
   |
   | /api/*
   v
Backend :3000
   |
   v
PyTorch AQI prediction models
```

## AQI Categories

The backend maps the model output to one of the following AQI categories:

| Class | AQI Status |
| --- | --- |
| 0 | Good |
| 1 | Moderate |
| 2 | USG |
| 3 | Unhealthy |
| 4 | Very Unhealthy |
| 5 | Severe |

## Run With Docker Compose

From the project root, run:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8000
```

Nginx exposes the application on port `8000`.

## Deploy To Cloud Run

This repository includes a Cloud Run specific container build:

- `cloud-run/Dockerfile` builds the Vue app as static files.
- The same container starts FastAPI on an internal port and Nginx on Cloud Run's `$PORT`.
- Nginx serves the frontend and proxies `/api/*` to FastAPI.
- `cloud-run/cloudbuild.yaml` builds, pushes, and deploys the container for CI/CD.

### One-Time Google Cloud Setup

Set your project and create an Artifact Registry repository:

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud artifacts repositories create cloud-run-source-deploy \
  --repository-format=docker \
  --location=asia-east1
```

The Cloud Build service account needs permission to push images and deploy Cloud Run services. If deployment fails with IAM errors, grant the Cloud Build service account these roles:

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

Make sure the required `.pkl` model files are present in `backend/` before deployment.

### Manual Deploy

From the project root:

```bash
gcloud builds submit \
  --config cloud-run/cloudbuild.yaml \
  --substitutions _REGION=asia-east1,_SERVICE_NAME=vqaweb,_AR_REPOSITORY=cloud-run-source-deploy
```

Change `_REGION`, `_SERVICE_NAME`, and `_AR_REPOSITORY` if your Google Cloud project uses different names.

### CI/CD With Cloud Build

Create a Cloud Build trigger that runs on push to your main branch and uses:

```text
cloud-run/cloudbuild.yaml
```

Recommended trigger substitutions:

| Name | Example |
| --- | --- |
| `_REGION` | `asia-east1` |
| `_SERVICE_NAME` | `vqaweb` |
| `_AR_REPOSITORY` | `cloud-run-source-deploy` |

Each push builds `cloud-run/Dockerfile`, pushes the image to Artifact Registry, and deploys it to Cloud Run.

### Local Docker CI With GitHub Actions

The repository also includes:

```text
.github/workflows/deploy-cloud-run.yml
```

This workflow runs when code is pushed to the `AQI` branch. It does not deploy to Cloud Run. It builds the local Docker Compose setup, starts it, and checks:

```text
http://localhost:8080/api/health
```

Cloud Run deployment is handled by the Cloud Build trigger. GitHub Actions is only used as a local-container CI check.

### Test The Cloud Run Image Locally

The easiest local test uses the same single-container image as Cloud Run:

```bash
docker compose -f local-run/docker-compose.yml up --build
```

Then open:

```text
http://localhost:8080
```

Health check:

```bash
curl http://localhost:8080/api/health
```

Stop it with:

```bash
docker compose -f local-run/docker-compose.yml down
```

You can also build and run the image directly:

```bash
docker build -f cloud-run/Dockerfile -t vqaweb-cloudrun .
docker run --rm -p 8080:8080 -e PORT=8080 vqaweb-cloudrun
```

Then open:

```text
http://localhost:8080
```

## Backend API

### GET `/api/health`

Returns:

```json
{
  "status": "ok"
}
```

### POST `/api/predict`

The frontend sends a multipart form request with:

| Field | Description |
| --- | --- |
| `image` | Uploaded image file |
| `rh` | Relative humidity |
| `rainfall` | Rainfall amount |
| `temperature` | Temperature |
| `wd_hr` | Wind direction |
| `ws_hr` | Wind speed |
| `model_name` | Model code, such as `A`, `B`, or `E` |

Example response:

```json
{
  "AQI": "Moderate",
  "pred_class": 1,
  "regression_value": 1.234,
  "description": "Air quality is acceptable; however, some pollutants may be a moderate health concern."
}
```

## Development Notes

### Backend

The backend uses FastAPI and runs on port `3000` inside Docker.

Main file:

```text
backend/main.py
```

### Frontend

The frontend uses Vue 3 and Vite. It runs on port `8000` inside Docker.

Main page:

```text
frontend/Present/src/pages/Normal.vue
```

### Nginx

Nginx routes normal page requests to the frontend and `/api/` requests to the backend.

Main config:

```text
nginx/conf.d/default.conf
```

## Notes

- The trained `.pkl` model files must exist in the `backend` directory before running the backend.
- Some training and preprocessing utilities are stored in `backend/fed_multimodal_restcol`.
- If model weights or pretrained torchvision weights are missing, the backend may need network access or local cached weights.
- Sensitive keys should not be committed directly in source code. Use environment variables for credentials.
