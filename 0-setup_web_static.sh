#!/usr/bin/env bash
# Sets up the web servers for the deployment of web_static.

if ! command -v nginx > /dev/null 2>&1; then
    apt-get update -y
    apt-get install -y nginx
fi

mkdir -p /data/web_static/releases/test /data/web_static/shared

cat > /data/web_static/releases/test/index.html << 'EOF'
<html>
  <head>
  </head>
  <body>
    Holberton School
  </body>
</html>
EOF

rm -f /data/web_static/current
ln -s /data/web_static/releases/test /data/web_static/current

chown -R ubuntu:ubuntu /data

config=/etc/nginx/sites-available/default
if ! grep -q 'hbnb_static' "$config"; then
    sed -i '0,/^[[:space:]]*server_name .*;/s//&\n\n    location \/hbnb_static {\n        alias \/data\/web_static\/current\/;\n    }/' "$config"
fi

service nginx restart

exit 0
