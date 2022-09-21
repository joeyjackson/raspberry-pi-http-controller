# Raspberry Pi HTTP Controller
NOTE: This was designed and tested to run on a Raspberry Pi Zero W. Other models may require changes to the docker build process, specifically using a different base image.

## Setup
### Hardware
The hardware configuration in this repo uses pin 40 (GPIO 21) connected to an LED but this setup should be easily extensible to other hardware devices or pins.

![Raspberry Pi Zero Pinout](pinout.png?raw=true "Raspberry Pi Zero Pinout")

[https://pinout.xyz/](https://pinout.xyz/)

### Configure Admin User
Create `.env` file with variables from `.sample-env`

### (Optional) Test
```
docker run --env-file=.env --rm --privileged -p 5000:5000 -d --name=controller raspberry-pi-http-controller
```

### Deploy with Nginx
See https://github.com/joeyjackson/docker-nginx-certbot-route53#connecting-with-other-docker-compose-apps
```
$ docker-compose -f path/to/other/app/docker-compose.yml -f compose-override/docker-compose.override.yml up -d
$ docker-compose -f docker-compose.yml -f compose-override/docker-compose.override.yml up -d
```