FROM node:22-bookworm-slim AS deps
WORKDIR /app
RUN npm install --global pnpm@9.15.4
COPY package.json pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/package.json
COPY packages/text-cleaner/package.json packages/text-cleaner/package.json
RUN pnpm install --no-frozen-lockfile

FROM node:22-bookworm-slim AS builder
WORKDIR /app
RUN npm install --global pnpm@9.15.4
COPY --from=deps /app /app
COPY . .
RUN pnpm --filter @cleanmark/web build

FROM node:22-bookworm-slim AS runner
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000
WORKDIR /app
RUN npm install --global pnpm@9.15.4
COPY --from=builder --chown=node:node /app /app
USER node
EXPOSE 3000
CMD ["pnpm", "--filter", "@cleanmark/web", "start"]
