# ─── Stage 1 : développement (hot reload Vite) ────────
FROM node:22-alpine3.21 AS development

WORKDIR /app

COPY package*.json ./
# npm install (pas npm ci) car package-lock.json sera généré au 1er run
RUN npm install

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ─── Stage 2 : builder (build de production) ──────────
FROM node:22-alpine3.21 AS builder

WORKDIR /app

COPY package*.json ./
# npm install ici aussi — npm ci sera activé dès que le lock file existera
RUN npm install

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# ─── Stage 3 : production (nginx léger) ───────────────
FROM nginx:1.27.5-alpine3.21 AS production

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]