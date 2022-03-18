FLASK_APP=duma_backend
FLASK_ENV=development

DUMA_BACKEND_SETTINGS=development.cfg

# TODO: move this into development.cfg?
#       it's secrets ... would be much better to fake it away somehow
DUMA_BACKEND_OIDC_DISCOVERY_URL='https://auth-test.tern.org.au/auth/realms/local/.well-known/openid-configuration'
DUMA_BACKEND_OIDC_CLIENT_ID=dst
DUMA_BACKEND_OIDC_CLIENT_SECRET=
DUMA_BACKEND_OIDC_USE_REFRESH_TOKEN=True