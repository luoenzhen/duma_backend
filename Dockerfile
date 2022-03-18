ARG ALPINE_VERSION=3.13

# BUILD and install code
FROM alpine:${ALPINE_VERSION} as builder

# Install build dependencies
RUN apk add --no-cache \
  git \
  python3 \
  python3-dev \
  g++

# Pkgs hard / slow / annoying to build from sourc (also those of which version does not matter too much)
RUN apk add --no-cache \
  py3-cryptography \
  py3-redis

# Create virtualenv to use for our app
RUN python3 -m venv --system-site-packages /opt/venv

# Configure virtualenv as default
ENV VIRTUALENV=/opt/venv \
  PATH=/opt/venv/bin:${PATH}

# Install and upgrade python deps in virtuaelenv
RUN pip install --no-cache-dir --upgrade \
  pip \
  setuptools \
  wheel

# Install deployment pkg needed
RUN pip install --no-cache-dir \
  gunicorn

# install dependencies
COPY requirements.txt /workspace/requirements.txt
RUN pip install -r /workspace/requirements.txt

# COPY source code into container
COPY dist/ /workspace/dist/
# Install pkg
RUN pip install --no-cache-dir /workspace/dist/*.whl





# BUILD space optimised final image, based on installed code from builder
FROM alpine:${ALPINE_VERSION} as runner

# # create app user and group
RUN addgroup -g 1000 duma_backend \
  && adduser -h /opt/venv -g 'duma_backend' -G duma_backend -D -H -u 1000 duma_backend

# Binary pkgs and other pkgs hard or slow to install from source
RUN apk add --no-cache \
  python3 \
  py3-cryptography \
  py3-psycopg2 \
  py3-redis

COPY --from=builder /opt/venv/ /opt/venv/

# Configure virtualenv as default
ENV VIRTUALENV=/opt/venv \
  PATH=/opt/venv/bin:${PATH}

# install entrypoint script
COPY build-files/docker_entrypoint.sh /docker_entrypoint.sh

# set default env for flask app
ENV FLASK_APP=duma_backend \
  FLASK_ENV=production

USER 1000

# TODO: setup ENTRYPOINT if needed and default CMD
ENTRYPOINT ["/docker_entrypoint.sh"]

# CMD ["gunicorn", "--bind=:5000", "--workers=2", "--threads=4", "--forwarded-allow-ips='*'",  "--statsd-host=statsd-exporter.services:9125", "--statsd-prefix=ecoimages_portal_api", "duma_backend:create_app()"]

CMD ["gunicorn", "--bind=:5000", "--forwarded-allow-ips='*'",  "duma_backend:create_app()"]
