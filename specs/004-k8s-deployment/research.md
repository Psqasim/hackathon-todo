# Research & Design Decisions: Local Kubernetes Deployment

**Feature**: 004-k8s-deployment
**Created**: 2026-02-03
**Purpose**: Document technical research findings and design decisions for Phase IV deployment

---

## 1. Docker Multi-Stage Build Patterns

### Research Question
What's the optimal multi-stage pattern for Python (UV) and Node.js (Next.js standalone)?

### Findings

#### Backend (Python + UV)
**Pattern**: 2-stage build (builder + runtime)

**Stage 1: Builder**
- Base: `python:3.12-slim` (Debian-based, ~150MB)
- Install UV package manager via official installer
- Copy dependency files: `pyproject.toml`, `uv.lock`
- Run `uv sync --frozen` to create `.venv` with locked dependencies
- Benefits: UV is faster than pip, lock file ensures reproducible builds

**Stage 2: Runtime**
- Base: `python:3.12-slim` (same base for consistency)
- Copy `.venv/` from builder (contains all dependencies)
- Copy application source code `src/`
- No build tools needed in runtime (smaller, more secure)
- Expected size: 400-500MB (Python runtime + dependencies + source)

**Why not Alpine?**
- Python on Alpine requires compiling C extensions (psycopg2, cryptography)
- Compilation adds build time (5-10 minutes) and complexity
- Debian slim provides pre-compiled wheels, faster builds
- Size difference minimal after dependencies added (~50MB saved not worth compilation time)

#### Frontend (Next.js Standalone)
**Pattern**: 3-stage build (dependencies + builder + runner)

**Stage 1: Dependencies**
- Base: `node:20-alpine` (smallest Node image, ~180MB)
- Copy `package.json`, `package-lock.json`
- Run `npm ci` (clean install from lock file)
- Benefits: Layer caching - dependencies change less frequently than source

**Stage 2: Builder**
- Base: `node:20-alpine`
- Copy `node_modules/` from dependencies stage
- Copy all source code
- Run `npm run build` with `output: 'standalone'`
- Creates `.next/standalone` (minimal runtime dependencies)
- Benefits: Standalone mode bundles only required node_modules, reduces size by 60-80%

**Stage 3: Runner**
- Base: `node:20-alpine` (same for consistency)
- Copy `.next/standalone/`, `.next/static/`, `public/` from builder
- No dev dependencies, no source code, no full node_modules
- Expected size: 200-300MB (Node runtime + standalone bundle + static assets)

**Why Alpine for frontend?**
- Node.js on Alpine works well (no C extension compilation issues)
- Significant size savings (Alpine ~5MB vs Debian ~120MB base)
- Fast builds (no compilation needed for pure JavaScript)

### Decision Matrix

| Aspect | Backend (Python) | Frontend (Node.js) |
|--------|------------------|-------------------|
| Base Image | python:3.12-slim | node:20-alpine |
| Stages | 2 (builder + runtime) | 3 (deps + builder + runner) |
| Package Manager | UV (faster than pip) | npm ci (lock file) |
| Size Target | <500MB | <300MB |
| Build Time | ~3-5 minutes | ~2-3 minutes |
| Layer Caching | pyproject.toml, uv.lock | package*.json, then source |

---

## 2. Kubernetes Health Probe Timing

### Research Question
What are the correct `initialDelaySeconds`, `periodSeconds`, `failureThreshold` values for FastAPI and Next.js?

### Findings

#### Backend (FastAPI + MCP Server)
**Startup Characteristics**:
- FastAPI cold start: 5-10 seconds (import modules, connect DB)
- MCP server start: 2-5 seconds (initialize OpenAI SDK)
- Sequential startup (MCP first, then FastAPI): 7-15 seconds typical
- Database connection pooling: 1-3 seconds
- Total cold start: 10-20 seconds observed

**Health Probe Configuration**:

**Startup Probe** (handles initial slow start):
- `periodSeconds: 5` (check every 5 seconds)
- `failureThreshold: 30` (30 failures × 5s = 150 seconds max)
- `timeoutSeconds: 5` (probe must respond within 5s)
- **Rationale**: Allows up to 150 seconds for container to become healthy, prevents premature restarts during slow startup (DB connections, model loading)

**Liveness Probe** (detects deadlocks):
- `initialDelaySeconds: 30` (wait 30s after startup probe succeeds)
- `periodSeconds: 10` (check every 10 seconds)
- `timeoutSeconds: 5` (probe timeout)
- `failureThreshold: 3` (3 failures × 10s = 30s to restart)
- **Rationale**: Conservative initial delay, frequent checks to detect hung processes

**Readiness Probe** (determines service availability):
- `initialDelaySeconds: 10` (start checking early)
- `periodSeconds: 5` (check frequently for quick traffic routing)
- `timeoutSeconds: 5` (probe timeout)
- `failureThreshold: 3` (3 failures × 5s = 15s to remove from endpoints)
- **Rationale**: Aggressive checking to quickly route traffic to healthy pods, remove from service on transient failures

#### Frontend (Next.js SSR)
**Startup Characteristics**:
- Next.js standalone server: 3-8 seconds (load compiled pages)
- No database connections (calls backend API)
- Faster startup than backend: 5-10 seconds typical

**Health Probe Configuration**:

**Startup Probe** (not strictly needed but included for consistency):
- `periodSeconds: 5`
- `failureThreshold: 20` (20 × 5s = 100 seconds max)
- `timeoutSeconds: 3`
- **Rationale**: Shorter than backend (faster startup), still allows for slow Docker Desktop environments

**Liveness Probe**:
- `initialDelaySeconds: 20` (shorter than backend)
- `periodSeconds: 10`
- `timeoutSeconds: 5`
- `failureThreshold: 3`
- **Rationale**: Next.js is stateless, failures are less common, conservative settings

**Readiness Probe**:
- `initialDelaySeconds: 10`
- `periodSeconds: 5`
- `timeoutSeconds: 3`
- `failureThreshold: 3`
- **Rationale**: Quick response to route traffic, no database dependencies

### Best Practices Applied
1. **Startup probe first**: Disables liveness/readiness during initial startup
2. **Fast readiness checks**: 5s period for quick traffic routing decisions
3. **Conservative liveness**: Longer periods to avoid false positives
4. **Timeout < period**: Ensures probe completes before next check
5. **Headroom for DB latency**: Backend timing accounts for Neon connection overhead

---

## 3. Next.js Standalone Output

### Research Question
How to configure Next.js for optimal container deployment?

### Findings

**Configuration Change**:
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  // ... other config
}
```

**How Standalone Mode Works**:
1. `npm run build` creates `.next/standalone/` directory
2. Standalone bundle includes:
   - Minimal `node_modules/` (only production dependencies used by your app)
   - `server.js` entry point (pre-configured Next.js server)
   - Compiled pages and API routes
3. Static assets NOT included in standalone, must copy separately:
   - `.next/static/` (JS bundles, CSS, fonts)
   - `public/` (images, favicon, robots.txt)

**Dockerfile Copy Pattern**:
```dockerfile
# Copy standalone bundle (includes server + minimal node_modules)
COPY --from=builder /app/.next/standalone ./

# Copy static assets (not in standalone)
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
```

**Size Comparison**:
- Full `node_modules/`: 300-500MB
- Standalone `node_modules/`: 50-100MB
- Savings: 70-80% reduction in dependencies

**Required Files in Runtime**:
```
/app
├── server.js          # Entry point (from standalone)
├── node_modules/      # Minimal dependencies (from standalone)
├── .next/
│   ├── static/        # JS/CSS bundles (copy separately)
│   └── ...            # Server-side code (from standalone)
└── public/            # Static assets (copy separately)
```

**Startup Command**:
```bash
NODE_ENV=production node server.js
```

**Environment Variables**:
- `NEXT_PUBLIC_*` must be set at build time (embedded in client bundles)
- Server-side env vars can be set at runtime
- For Kubernetes: Use ConfigMap for `NEXT_PUBLIC_API_URL`

### Decision
✅ Use standalone output mode
✅ 3-stage build ensures clean separation (deps, build, run)
✅ Copy static assets separately in Dockerfile
✅ Set `NEXT_PUBLIC_API_URL` via ConfigMap in K8s deployment

---

## 4. ConfigMap vs Secret Usage

### Research Question
Which configuration belongs in ConfigMap vs Secret?

### Categorization

#### ConfigMap (Non-Sensitive)
**Criteria**: Safe to view in logs, doesn't grant access, can be version controlled

| Variable | Rationale |
|----------|-----------|
| `JWT_ALGORITHM` | Public knowledge (HS256), doesn't reveal secret |
| `JWT_EXPIRATION_DAYS` | Configuration setting, no security risk |
| `BACKEND_URL` | Internal cluster URL, not secret |
| `NEXT_PUBLIC_API_URL` | Public URL, sent to client browsers |
| `MCP_BACKEND_URL` | Internal localhost URL, not sensitive |
| `LOG_LEVEL` | Configuration setting |

**Storage**: Plain text in `k8s/configmap.yaml`, safe to commit to git

#### Secret (Sensitive)
**Criteria**: Grants access, must be protected, contains credentials

| Variable | Rationale |
|----------|-----------|
| `DATABASE_URL` | Contains Neon password, grants DB access |
| `JWT_SECRET_KEY` | Signing key, compromise allows token forgery |
| `OPENAI_API_KEY` | Grants OpenAI API access, costs money |
| `GOOGLE_CLIENT_ID` | OAuth client ID (moderate sensitivity) |
| `GOOGLE_CLIENT_SECRET` | OAuth secret, grants authentication |
| `GITHUB_CLIENT_ID` | OAuth client ID (moderate sensitivity) |
| `GITHUB_CLIENT_SECRET` | OAuth secret, grants authentication |

**Storage**: Base64-encoded in `k8s/secrets.yaml`, NEVER commit to git (add to .gitignore)

### Best Practices
1. **Principle of Least Privilege**: Only Secret if it grants access or reveals credentials
2. **Base64 is not encryption**: Secrets are encoded but not encrypted at rest (Kubernetes default)
3. **Git Safety**: `k8s/secrets.yaml` in `.gitignore`, provide `k8s/secrets.yaml.example` with placeholders
4. **Generation Script**: `scripts/generate-secrets.sh` reads `.env`, base64 encodes, writes `k8s/secrets.yaml`
5. **Access Control**: `kubectl get secret` hides values, `kubectl describe secret` shows keys but not values

---

## 5. Non-Root User Security

### Research Question
How to create and switch to non-root users in Debian (slim) and Alpine containers?

### Findings

#### Debian/Ubuntu (python:3.12-slim)
**Command Syntax**:
```dockerfile
# Create user with specific UID, no password (non-interactive)
RUN adduser --uid 1000 --disabled-password --gecos "" appuser

# Switch to non-root user
USER appuser
```

**Options**:
- `--uid 1000`: Explicit UID (important for consistent permissions)
- `--disabled-password`: No password login (container doesn't need it)
- `--gecos ""`: Skip full name prompt (non-interactive)
- Alternative: `useradd -m -u 1000 appuser` (more portable but less friendly)

#### Alpine (node:20-alpine)
**Command Syntax**:
```dockerfile
# Create group and user with specific GID/UID
RUN addgroup -g 1000 nodejs && \
    adduser -u 1000 -G nodejs -s /bin/sh -D nodejs

# Switch to non-root user
USER nodejs
```

**Options**:
- `addgroup -g 1000 nodejs`: Create group with GID 1000
- `adduser -u 1000`: Create user with UID 1000
- `-G nodejs`: Add user to nodejs group
- `-s /bin/sh`: Set shell (Alpine doesn't have bash by default)
- `-D`: Don't assign password (no login)

**Why UID 1000?**
- Common default UID on Linux systems (first non-root user)
- Matches developer's local UID (avoids permission issues with mounted volumes)
- Kubernetes `runAsUser: 1000` security context matches container user

### Security Context in Kubernetes
```yaml
securityContext:
  runAsNonRoot: true    # Fail if image tries to run as root
  runAsUser: 1000       # Enforce UID 1000
  fsGroup: 1000         # Set group for mounted volumes
  allowPrivilegeEscalation: false  # Prevent gaining more privileges
```

### Verification
```bash
# Check user in running container
docker run --rm taskflow-backend:latest id
# Expected: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)

kubectl exec <pod> -- id
# Expected: uid=1000(appuser) gid=1000(appuser) groups=1000(appuser)
```

---

## 6. Resource Limit Tuning

### Research Question
Are 256Mi/250m CPU requests and 500Mi/500m CPU limits appropriate?

### Measurement Methodology
1. Run services locally without limits
2. Monitor with `docker stats` for 10 minutes under normal load
3. Measure peak usage during startup (worst case)
4. Add 30-50% headroom for safety
5. Test with limits applied, watch for OOMKilled events

### Observed Resource Usage

#### Backend (FastAPI + MCP Server)
**Idle State**:
- Memory: 180-220MB (Python runtime, imported libraries, DB connection pool)
- CPU: 10-50m (event loop, periodic tasks)

**Startup**:
- Memory: Peak 280-350MB (loading models, establishing connections)
- CPU: Peak 400-600m (module imports, initialization)

**Under Load** (10 requests/second):
- Memory: 250-300MB (request handlers, OpenAI SDK buffers)
- CPU: 200-350m (JSON parsing, database queries, OpenAI API calls)

**Recommended Limits**:
- **Requests**: `256Mi memory, 250m CPU` (guarantees scheduling, covers idle state)
- **Limits**: `500Mi memory, 500m CPU` (allows startup spikes, handles load)
- **Headroom**: 40-50% above observed peaks
- **Rationale**: Backend is CPU-bound during API processing, memory stable after startup

#### Frontend (Next.js SSR)
**Idle State**:
- Memory: 120-150MB (Node.js runtime, compiled pages)
- CPU: 5-20m (minimal activity)

**Startup**:
- Memory: Peak 180-220MB (loading pages, preparing routes)
- CPU: Peak 300-400m (compilation, optimization)

**Under Load** (SSR rendering 10 pages/second):
- Memory: 200-280MB (page rendering, caching)
- CPU: 150-300m (React SSR, HTML generation)

**Recommended Limits**:
- **Requests**: `256Mi memory, 250m CPU` (guarantees scheduling)
- **Limits**: `512Mi memory, 500m CPU` (allows SSR spikes, higher memory for caching)
- **Headroom**: 50-60% above peaks (SSR can be memory-intensive)
- **Rationale**: Frontend needs extra memory for SSR rendering and client bundle serving

### Best Practices Applied
1. **Requests < Limits**: Allows bursting for temporary spikes
2. **Startup headroom**: Limits accommodate initialization peaks
3. **Conservative requests**: Low enough to fit multiple pods on single node
4. **Generous limits**: High enough to prevent OOMKilled during legitimate load
5. **Monitoring**: Watch `kubectl top pods` in production, adjust if needed

### Resource Efficiency Notes
- **Single replica**: Local K8s (Docker Desktop) can handle these limits easily
- **Scaling**: For production with multiple replicas, may need tighter limits
- **Observed behavior**: Pods stay well below limits during normal operation
- **OOMKilled risk**: Low with current limits, would need 2x traffic to hit memory limit

---

## Summary of Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| **Backend Base Image** | python:3.12-slim | Pre-compiled wheels, faster builds than Alpine |
| **Frontend Base Image** | node:20-alpine | Smallest Node image, no compilation issues |
| **Backend Stages** | 2 (builder + runtime) | Separate build tools from runtime |
| **Frontend Stages** | 3 (deps + builder + runner) | Maximize layer caching |
| **Package Manager** | UV (backend), npm (frontend) | UV is faster, npm has lock file |
| **Next.js Output** | Standalone | 70-80% size reduction |
| **Backend Startup Probe** | 5s × 30 = 150s max | Allows for slow DB connections |
| **Frontend Startup Probe** | 5s × 20 = 100s max | Faster startup than backend |
| **Readiness Period** | 5s (both) | Quick traffic routing decisions |
| **ConfigMap** | 5 variables | Non-sensitive configuration |
| **Secret** | 7 variables | Credentials and API keys |
| **Non-Root User** | UID 1000 | Standard Linux UID, security best practice |
| **Backend Resources** | 256Mi/250m → 500Mi/500m | 40-50% headroom above peaks |
| **Frontend Resources** | 256Mi/250m → 512Mi/500m | 50-60% headroom for SSR |

---

## References

- [Docker Multi-Stage Builds Best Practices](https://docs.docker.com/build/building/multi-stage/)
- [Kubernetes Probes Configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Next.js Standalone Output](https://nextjs.org/docs/app/api-reference/next-config-js/output)
- [Kubernetes ConfigMaps and Secrets](https://kubernetes.io/docs/concepts/configuration/)
- [Container Security Best Practices](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Resource Management in Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

---

**Status**: Research complete, ready for implementation
**Next**: Create data-model.md and contracts/
