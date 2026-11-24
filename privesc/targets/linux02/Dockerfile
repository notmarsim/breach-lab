FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash backup_user \
    && mkdir -p /opt/nexora/scripts \
    && echo '#!/usr/bin/env bash\necho "Backup cycle placeholder"' > /opt/nexora/scripts/nightly_backup.sh \
    && chmod 0755 /opt/nexora/scripts/nightly_backup.sh

USER backup_user
WORKDIR /home/backup_user
CMD ["sleep", "infinity"]
