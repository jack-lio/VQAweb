# AQIweb on k3s (Raspberry Pi)

Runs the Vue frontend on a Raspberry Pi with k3s. The PyTorch prediction
backend is **not deployed yet**: `/api/*` answers
`503 {"error": "AQI prediction backend is not available"}`.
Postgres + Airflow for the AQI data live in `~/sql-k8s/k3s`.

```text
Browser -> Traefik (Pi :80) -> aqi-frontend (nginx, static Vue build)
                                    | /api/*
                                    v
                               aqi-backend Service (no pods until backend.yaml is enabled)
```

Requires a 64-bit OS on the Pi (Raspberry Pi 4/5).

## One-time setup

On the Pi:

```bash
curl -sfL https://get.k3s.io | sh -
sudo k3s kubectl get nodes
```

On the build machine (WSL), copy the Pi's kubeconfig:

```bash
PI=192.168.1.50   # your Pi's IP
ssh pi@$PI sudo cat /etc/rancher/k3s/k3s.yaml | sed "s/127.0.0.1/$PI/" > ~/.kube/pi.yaml
chmod 600 ~/.kube/pi.yaml
KUBECONFIG=~/.kube/pi.yaml kubectl get nodes
```

Install buildx and arm64 emulation so this x86 machine can build ARM images:

```bash
sudo apt-get install docker-buildx
docker run --privileged --rm tonistiigi/binfmt --install arm64
docker buildx ls   # should list linux/arm64
```

## Deploy

```bash
PI_HOST=pi@192.168.1.50 ./k3s/deploy.sh
```

This builds the images for `linux/arm64`, imports them into the Pi's k3s with
`k3s ctr images import` (no registry needed), applies the manifests with
Kustomize and waits for the rollout. Open `http://<pi-ip>/`.

## Enabling the prediction backend later

1. Uncomment `- backend.yaml` in `kustomization.yaml`.
2. Run `deploy.sh` again; it then builds `backend/` too.

The backend needs about 1 GB of memory. `backend/requirements.txt` already
selects the right PyTorch wheels for ARM64.

## Files

| File | Purpose |
| --- | --- |
| `frontend.Dockerfile` | Builds the Vue app, serves it with nginx |
| `nginx/default.conf` | nginx config, mounted from a generated ConfigMap |
| `frontend.yaml` | Frontend Deployment + Service |
| `backend-service.yaml` | Backend Service, always deployed so nginx can start |
| `backend.yaml` | Backend Deployment, disabled for now |
| `ingress.yaml` | Traefik Ingress on port 80 |
| `kustomization.yaml` | Ties it together; `deploy.sh` updates the image tags |
