FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends openssh-server && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd \
    && useradd -m -s /bin/bash ops_ssh \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22
HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD pgrep -x sshd >/dev/null || exit 1
CMD ["/usr/sbin/sshd", "-D"]
