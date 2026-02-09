# JupyterHub Local

A dockerized JupyterHub setup with OAuth authentication, designed for local/on-premise deployment.

## Architecture

- **JupyterHub** (port 8080): Main hub that authenticates users and spawns individual Jupyter containers
- **DockerSpawner**: Spawns isolated JupyterLab containers per user on the `analytics_net` network
- **Generic OIDC**: Enterprise authentication via any OpenID Connect provider (Entra ID, Okta, Keycloak, etc.)

## Prerequisites

- Docker and Docker Compose
- OIDC client (i.e. Entra ID app registration)
- Network access to OIDC Client

## Quick Start

1. **Configure environment variables**

   Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

2. **Build the user notebook image**
   ```bash
   docker build -t my-custom-py-dev:latest -f Dockerfile.spawn .
   ```

3. **Start JupyterHub**
   ```bash
   docker-compose up -d
   ```

4. **Access the hub**

   Navigate to `https://<your-ip>:8080`

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OAUTH_CLIENT_ID` | OIDC client ID | Yes |
| `OAUTH_CLIENT_SECRET` | OIDC client secret | Yes |
| `OAUTH_CALLBACK_URL` | OAuth callback URL (e.g., `https://10.20.0.28:8080/hub/oauth_callback`) | Yes |
| `OAUTH_AUTHORIZE_URL` | OIDC authorization endpoint | Yes |
| `OAUTH_TOKEN_URL` | OIDC token endpoint | Yes |
| `OAUTH_USERDATA_URL` | OIDC userinfo endpoint | Yes |
| `OAUTH_USERNAME_CLAIM` | Claim to use as username | No (default: `email`) |
| `ALLOWED_USERS` | Comma-separated list of allowed user emails | Yes |
| `ADMIN_USERS` | Comma-separated list of admin user emails | Yes |
| `DOCKER_SPAWNER_NETWORK_NAME` | Docker network for spawned containers | No (default: `analytics_net`) |
| `HUB_CONNECT_IP` | Hostname spawned containers use to reach hub | No (default: `jupyterhub`) |
| `HUB_PORT` | Internal hub API port | No (default: `8081`) |

### OIDC Setup (Entra ID Example)

1. Register an application in Azure Portal
2. Set redirect URI to: `https://<your-ip>:8080/hub/oauth_callback`
3. Create a client secret
4. Grant `User.Read` API permission
5. Configure `.env` with:
   - `OAUTH_AUTHORIZE_URL=https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/authorize`
   - `OAUTH_TOKEN_URL=https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token`
   - `OAUTH_USERDATA_URL=https://graph.microsoft.com/oidc/userinfo`

## Project Structure

```
jupyterhub-local/
├── docker-compose.yml      # Orchestrates the hub container
├── Dockerfile.hub          # JupyterHub image with OAuth + DockerSpawner
├── Dockerfile.spawn        # User notebook image with data science packages
├── jupyterhub_config.py    # Hub configuration (reads from env vars)
├── requirements.txt        # Python packages for user notebooks
├── .env                    # Environment variables (not in git)
├── certs/                  # SSL certificates (auto-generated)
└── jupyterhub_data/        # Persistent hub data
```

## User Notebook Environment

The spawned containers include:

- **JupyterLab 4.5**
- **Data Science**: numpy, pandas, scipy, scikit-learn
- **Visualization**: matplotlib, seaborn, plotly
- **Database**: sqlalchemy, psycopg (PostgreSQL)
- **Utilities**: pyarrow, openpyxl, tqdm

## Adding New Libraries

To add Python packages for data analysis:

1. Edit `requirements.txt` and add your packages:
   ```
   # Example additions
   statsmodels==0.14.1
   xgboost==2.0.3
   networkx==3.2.1
   ```

2. Rebuild the notebook image:
   ```bash
   docker build -t my-custom-py-dev:latest -f Dockerfile.spawn .
   ```

3. Restart user containers (users must stop and restart their servers from the JupyterHub control panel, or an admin can restart them)

**Tips:**
- Pin versions (e.g., `pandas==3.0.0`) for reproducibility
- Test locally first: `pip install <package>` in a notebook cell to verify compatibility
- For packages requiring system dependencies, modify `Dockerfile.spawn` to add them via `apt-get`

## Rebuilding Images

After modifying `requirements.txt` or `Dockerfile.spawn`:
```bash
rebuild-base-image.cmd
```

Or manually:
```bash
docker build -t my-custom-py-dev:latest -f Dockerfile.spawn .
docker-compose up -d --force-recreate
```

## SSL Certificates

Self-signed certificates are auto-generated on first startup in the `certs/` directory. For production, replace with proper certificates.

## Troubleshooting

**Spawned container can't connect to hub**
- Ensure `HUB_CONNECT_IP` matches the hub container name
- Verify both containers are on the same Docker network

**OAuth callback fails**
- Check `OAUTH_CALLBACK_URL` matches your server IP and port
- Verify the redirect URI is registered in your OIDC provider

**Permission denied errors**
- Ensure Docker socket is mounted: `/var/run/docker.sock`
