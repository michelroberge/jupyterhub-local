import os
from oauthenticator.generic import GenericOAuthenticator
import dockerspawner

def clean_username(name):
    return name.replace('@', '_').replace('.', '_')

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
