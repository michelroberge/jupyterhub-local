import os
import shutil
from pathlib import Path
from oauthenticator.generic import GenericOAuthenticator
import dockerspawner

def clean_username(name):
    return name.replace('@', '_').replace('.', '_')


async def pre_spawn_hook(spawner):
    """Initialize user directory before spawning container."""
    username = spawner.user.name
    safe_username = clean_username(username)

    # Paths inside the JupyterHub container (for file operations)
    hub_data_path = Path('/srv/jupyterhub/data')
    hub_workspaces_path = Path('/srv/jupyterhub/workspaces')
    user_dir = hub_data_path / safe_username
    default_workspace = hub_workspaces_path / 'default'

    spawner.log.info(f"Pre-spawn hook for user: {username} (sanitized: {safe_username})")

    # HOST_DATA_PATH must be an absolute Windows path like: C:/dev/jupyterhub-local/jupyterhub_data
    # This is required because DockerSpawner mounts volumes from the HOST perspective
    host_data_path = os.environ.get('HOST_DATA_PATH')
    if not host_data_path:
        raise ValueError("HOST_DATA_PATH environment variable must be set to an absolute Windows path (e.g., C:/dev/jupyterhub-local/jupyterhub_data)")

    # Ensure forward slashes for Docker on Windows
    host_data_path = host_data_path.replace('\\', '/')

    spawner.volumes = {
        f'{host_data_path}/{safe_username}': '/home/jovyan/work'
    }
    spawner.log.info(f"Volume mount: {host_data_path}/{safe_username} -> /home/jovyan/work")

    # Ensure user directory exists
    user_dir.mkdir(parents=True, exist_ok=True)

    # Always copy default workspace (tutorials) - overwrites existing files
    if default_workspace.exists():
        spawner.log.info(f"Copying default workspace from {default_workspace} to {user_dir}")
        shutil.copytree(default_workspace, user_dir, dirs_exist_ok=True)
        spawner.log.info("Default workspace copied/updated successfully")
    else:
        spawner.log.warning(f"Default workspace not found at {default_workspace}")

    # Set ownership to jovyan user (UID 1000, GID 100)
    try:
        for root, dirs, files in os.walk(user_dir):
            os.chown(root, 1000, 100)
            for d in dirs:
                os.chown(os.path.join(root, d), 1000, 100)
            for f in files:
                os.chown(os.path.join(root, f), 1000, 100)
        spawner.log.info(f"Permissions set for {safe_username}")
    except OSError as e:
        spawner.log.warning(f"Could not set ownership (expected on Windows): {e}")


# --- 1. CORE SPAWNER CONFIG ---
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.name_template = 'jupyter-{username}'
c.DockerSpawner.debug = True
c.DockerSpawner.notebook_dir = '/home/jovyan/work'
c.DockerSpawner.default_url = '/lab'
c.DockerSpawner.image = 'my-custom-py-dev:latest'
c.DockerSpawner.pull_policy = 'ifnotpresent'
c.DockerSpawner.remove = False
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = os.environ.get('DOCKER_SPAWNER_NETWORK_NAME', 'analytics_net')

# Register pre-spawn hook (volumes are set dynamically in the hook)
c.Spawner.pre_spawn_hook = pre_spawn_hook


# Hub connection settings - THIS IS CRITICAL
c.JupyterHub.hub_connect_ip = os.environ.get('HUB_CONNECT_IP', 'jupyterhub')
c.JupyterHub.hub_ip = os.environ.get('HUB_IP', '0.0.0.0')
c.JupyterHub.hub_connect_url = os.environ.get('HUB_CONNECT_URL', 'http://jupyterhub:8081')
c.JupyterHub.hub_port = int(os.environ.get('HUB_PORT', '8081'))

# --- 2. AUTHENTICATOR CONFIG (Generic OIDC) ---
c.JupyterHub.authenticator_class = GenericOAuthenticator
c.GenericOAuthenticator.client_id = os.environ['OAUTH_CLIENT_ID']
c.GenericOAuthenticator.client_secret = os.environ['OAUTH_CLIENT_SECRET']
c.GenericOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GenericOAuthenticator.authorize_url = os.environ['OAUTH_AUTHORIZE_URL']
c.GenericOAuthenticator.token_url = os.environ['OAUTH_TOKEN_URL']
c.GenericOAuthenticator.userdata_url = os.environ['OAUTH_USERDATA_URL']
c.GenericOAuthenticator.scope = ['openid', 'email', 'profile']
c.GenericOAuthenticator.username_claim = os.environ.get('OAUTH_USERNAME_CLAIM', 'email')

# --- 3. HUB NETWORK & SSL ---
c.JupyterHub.ssl_key = os.environ.get('SSL_KEY_PATH', '/app/certs/key.pem')
c.JupyterHub.ssl_cert = os.environ.get('SSL_CERT_PATH', '/app/certs/cert.pem')
c.ConfigurableHTTPProxy.api_url = os.environ.get('PROXY_API_URL', 'http://127.0.0.1:8001')
c.JupyterHub.bind_url = os.environ.get('HUB_BIND_URL', 'https://0.0.0.0:8000')

# Access Control
allowed_users = os.environ.get('ALLOWED_USERS', '')
c.Authenticator.allowed_users = set(allowed_users.split(',')) if allowed_users else set()

admin_users = os.environ.get('ADMIN_USERS', '')
c.GenericOAuthenticator.admin_users = set(admin_users.split(',')) if admin_users else set()
