#!/bin/sh

# this script assumes that there is a postgres service setup in your bitbucket pipeline build step

IMAGE_NAME=$1
CONTAINER_NAME=duma_backend

# start up image
docker run -d -p 5000:5000 \
    --name $CONTAINER_NAME \
    -e DUMA_BACKEND_SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@postgres/postgres \
    -e DUMA_BACKEND_OIDC_DISCOVERY_URL=http://localhost:5000/ \
    --add-host postgres:$BITBUCKET_DOCKER_HOST_INTERNAL \
    $IMAGE_NAME \
    gunicorn --bind :5000 --workers=1 --threads=2 'duma_backend:create_app()'

# connect to _health endpoint
wget -O - --content-on-error -q --tries 5 --retry-connrefused http://localhost:5000/api/_health
result=$?

# show container logs (help to find out problems)
docker logs $CONTAINER_NAME

# tear down container
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

# exit with curl exit status
exit $result
