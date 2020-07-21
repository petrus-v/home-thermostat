# Thermostatic relay

## POCS

Build docker image:

```bash
docker build -t lamp .
```

### POC scaleway iot hub

```bash
docker run --rm -it \
    -v /home/pirate/lamp/:/srv
    lamp python /srv/src/iot-mqtt.py
```

### POC turn ON/OFF the light

run turn on/off the light in docker container

```bash
docker run --rm -it --device /dev/gpiomem \
    -v /home/pirate/lamp/:/srv
    lamp python /srv/src/relays.py
```
