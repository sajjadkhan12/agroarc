# AgroArc frontend image
# Multi-stage: Vite build (Node), static assets served by Nginx.
#   docker build -t agroarc-frontend:latest ./frontend

FROM node:20-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --ignore-scripts

COPY index.html index.tsx App.tsx types.ts vite.config.ts tsconfig.json vite-env.d.ts ./
COPY components ./components
COPY services ./services

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Typecheck runs in CI; Docker only produces the production bundle.
RUN --mount=type=cache,target=/root/.npm \
    npx vite build \
    && rm -rf node_modules

FROM nginx:1.27-alpine AS runtime

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1/healthz >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]
