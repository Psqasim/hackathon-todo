# Multi-stage Dockerfile for Next.js frontend - Kubernetes deployment
# Optimized for production with standalone output and minimal size

# ============================================================================
# Stage 1: Dependencies - Install node_modules
# ============================================================================
FROM node:20-alpine AS dependencies

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies from lock file (clean install)
RUN npm ci

# ============================================================================
# Stage 2: Builder - Build Next.js application
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy node_modules from dependencies stage
COPY --from=dependencies /app/node_modules ./node_modules

# Copy application source
COPY . .

# Accept build arguments for Next.js public environment variables
# These get embedded in the client-side JavaScript bundle
ARG NEXT_PUBLIC_API_URL=http://backend-service:8000
ARG NEXT_PUBLIC_CHAT_ENABLED=true

# Set as environment variables for the build process
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_CHAT_ENABLED=$NEXT_PUBLIC_CHAT_ENABLED \
    NEXT_TELEMETRY_DISABLED=1

# Build Next.js application with standalone output
# This creates .next/standalone with minimal dependencies
RUN npm run build

# ============================================================================
# Stage 3: Runner - Minimal production image
# ============================================================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set Node environment to production
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Note: node:20-alpine already includes a 'node' user with UID 1000
# We'll use that instead of creating a new user

# Copy standalone output from builder
# Standalone includes minimal node_modules and server
COPY --from=builder --chown=node:node /app/.next/standalone ./

# Copy static assets (not included in standalone)
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public

# Switch to non-root user (node user with UID 1000)
USER node

# Expose port 3000
EXPOSE 3000

# Health check for Kubernetes probes
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -q -O /dev/null http://localhost:3000/ || exit 1

# Start Next.js standalone server
CMD ["node", "server.js"]
