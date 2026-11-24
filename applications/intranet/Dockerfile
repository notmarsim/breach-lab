FROM php:8.3-apache
COPY index.php /var/www/html/index.php
EXPOSE 80
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD curl -fsS http://127.0.0.1/?health=1 >/dev/null || exit 1
