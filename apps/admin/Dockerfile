# Multi-stage production Dockerfile for Menu-It Admin Frontend (FCD-12 WP-11)
FROM node:22-alpine AS builder
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@11.11.0 --activate

COPY pnpm-lock.yaml pnpm-workspace.yaml package.json ./
COPY packages/ ./packages/
COPY apps/admin/ ./apps/admin/

RUN pnpm install --frozen-lockfile
RUN pnpm --filter @menu-it/admin build

FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3001 \
    HOSTNAME=0.0.0.0

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder --chown=appuser:appgroup /app/apps/admin/.next/standalone ./
COPY --from=builder --chown=appuser:appgroup /app/apps/admin/.next/static ./apps/admin/.next/static
COPY --from=builder --chown=appuser:appgroup /app/apps/admin/public ./apps/admin/public

USER appuser

EXPOSE 3001

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3001/ || exit 1

CMD ["node", "apps/admin/server.js"]
