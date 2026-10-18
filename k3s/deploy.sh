#!/usr/bin/env bash
# Build ARM64 images on this machine, copy them into k3s on the Raspberry Pi,
# and apply the manifests. No container registry is needed.
#
# Usage: PI_HOST=pi@192.168.1.50 ./k3s/deploy.sh [tag]
#
# Needs on this machine: docker buildx with QEMU arm64 emulation, kubectl, and
# the Pi's kubeconfig at $PI_KUBECONFIG (see k3s/README.md).
# Needs on the Pi: passwordless sudo for PI_HOST (the Raspberry Pi OS default).
set -euo pipefail

PI_HOST="${PI_HOST:?set PI_HOST, e.g. PI_HOST=pi@192.168.1.50}"
PLATFORM="${PLATFORM:-linux/arm64}"
export KUBECONFIG="${PI_KUBECONFIG:-$HOME/.kube/pi.yaml}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TAG="${1:-$(git -C "$ROOT" rev-parse --short HEAD)}"

images=(aqi-frontend)
if grep -q '^  - backend.yaml' "$ROOT/k3s/kustomization.yaml"; then
    images+=(aqi-backend)
fi

echo "==> Building ${images[*]} ($PLATFORM, tag $TAG)"
docker buildx build --platform "$PLATFORM" --load \
    -f "$ROOT/k3s/frontend.Dockerfile" \
    -t "aqi-frontend:$TAG" "$ROOT/frontend/Present"
if [[ " ${images[*]} " == *" aqi-backend "* ]]; then
    docker buildx build --platform "$PLATFORM" --load \
        -t "aqi-backend:$TAG" "$ROOT/backend"
fi

echo "==> Importing images into k3s on $PI_HOST"
docker save "${images[@]/%/:$TAG}" | ssh "$PI_HOST" sudo k3s ctr images import -

echo "==> Applying manifests"
sed -i "s/newTag: .*/newTag: $TAG/" "$ROOT/k3s/kustomization.yaml"
kubectl apply -k "$ROOT/k3s"

for image in "${images[@]}"; do
    kubectl -n aqi rollout status "deploy/$image" --timeout=10m
done

echo "==> Done: http://${PI_HOST#*@}/"
