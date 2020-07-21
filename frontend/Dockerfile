FROM node:14-buster-slim as dev

WORKDIR /usr/frontend

RUN apt-get update && apt-get install -y gettext

COPY package*.json ./

RUN npm ci

EXPOSE 3000

COPY . .

RUN npm run build

CMD ["npm", "run", "serve"]

FROM caddy:2-alpine

ENV ENVSUBST_VERSION="v1.1.0"

RUN apk update \
    && apk add curl \
    && curl -L https://github.com/a8m/envsubst/releases/download/$ENVSUBST_VERSION/envsubst-Linux-x86_64 -o /usr/local/bin/envsubst \
    && chmod +x /usr/local/bin/envsubst \
    && apk del curl \
    && mkdir /srv/frontend/

COPY --from=dev /usr/frontend/dist /srv/frontend/
COPY reverse-proxy/Caddyfile.template /etc/caddy/Caddyfile.template
COPY reverse-proxy/entrypoint.sh /usr/bin/entrypoint.sh

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
