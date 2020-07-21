#!/bin/sh

file=/etc/caddy/Caddyfile.template
echo "Generate ${file%.*} using template: $file"
envsubst -i $file > ${file%.*}

exec /usr/bin/caddy run -config /etc/caddy/Caddyfile
