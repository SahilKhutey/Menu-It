# Multi-stage production Dockerfile for Menu-It Web Frontend (FCD-12 WP-11)
FROM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@11.11.0 --activate

COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY packages/ ./packages/
COPY apps/web/ ./apps/web/
COPY apps/admin/package.json ./apps/admin/package.json

RUN pnpm install --frozen-lockfile
RUN pnpm --filter @menu-it/web build

FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/apps/web/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=builder --chown=appuser:appgroup /app/apps/web/public ./apps/web/public

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

CMD ["node", "apps/web/server.js"]
