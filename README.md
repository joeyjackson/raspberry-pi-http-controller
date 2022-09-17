# Raspberry Pi HTTP Controller
NOTE: This was designed and tested to run on a Raspberry Pi Zero W. Other models may require changes to the docker build process, specifically using a different base image.

## Build
```
docker build -t raspberry-pi-http-controller .
```

## Configure Admin User
Create .env file with variables from .sample-env

## Test
```
docker run --env-file=.env --rm --privileged -p 5000:5000 --name=controller raspberry-pi-http-controller
```

## Deploy with Nginx
See https://github.com/joeyjackson/docker-nginx-certbot-route53#connecting-with-other-docker-compose-apps
```
docker compose -f docker-compose.yml -f compose-override/docker-compose.override.yml up -d
```
```
docker run --env-file=.env --restart unless-stopped --privileged --network="nginx-shared" -d --name=controller raspberry-pi-http-controller
```