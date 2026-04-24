ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    iputils \
    net-tools \
    nmap \
    curl \
    jq \
    py3-pip

COPY rootfs/requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY rootfs/app/ /app/app/
COPY rootfs/main.py /app/main.py
COPY rootfs/static/ /app/static/
COPY rootfs/etc/ /etc/

RUN chmod +x /etc/services.d/network-monitor/run
