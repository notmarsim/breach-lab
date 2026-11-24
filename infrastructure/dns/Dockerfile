FROM ubuntu/bind9:9.18-24.04_beta

COPY named.conf.local /etc/bind/named.conf.local
COPY db.nexora.test /etc/bind/zones/db.nexora.test

EXPOSE 53/udp 53/tcp
