FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends sudo cron python3 && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash ops_user \
    && mkdir -p /opt/nexora/bin /var/lib/nexora \
    && echo '#!/bin/sh\necho "Nexora service status: OK"' > /opt/nexora/bin/check_status.sh \
    && chmod 0755 /opt/nexora/bin/check_status.sh

USER ops_user
WORKDIR /home/ops_user
CMD ["sleep", "infinity"]
