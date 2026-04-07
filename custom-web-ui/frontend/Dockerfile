FROM node:20-alpine AS deps
WORKDIR /app/custom-web-ui/frontend
COPY custom-web-ui/frontend/package*.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app/custom-web-ui/frontend
COPY --from=deps /app/custom-web-ui/frontend/node_modules ./node_modules
COPY custom-web-ui/frontend ./
RUN npm run build

FROM node:20-alpine AS runner
ENV NODE_ENV=production
WORKDIR /app/custom-web-ui/frontend
COPY --from=builder /app/custom-web-ui/frontend/.next ./.next
COPY --from=builder /app/custom-web-ui/frontend/public ./public
COPY --from=builder /app/custom-web-ui/frontend/package.json ./package.json
COPY --from=builder /app/custom-web-ui/frontend/node_modules ./node_modules
EXPOSE 3000

CMD ["npm", "run", "start", "--", "-p", "3000"]
