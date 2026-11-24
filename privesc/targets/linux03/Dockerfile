FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash svc_user \
    && mkdir -p /opt/nexora/app

USER svc_user
WORKDIR /home/svc_user
CMD ["sleep", "infinity"]
