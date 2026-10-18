# Build context: frontend/Present
# The build stage runs on the build machine's own platform; only the nginx
# stage targets the Raspberry Pi, so npm does not run under emulation.
FROM --platform=$BUILDPLATFORM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine

# /etc/nginx/conf.d is replaced by the aqi-frontend-nginx ConfigMap in k3s.
COPY --from=build /app/dist /usr/share/nginx/html
