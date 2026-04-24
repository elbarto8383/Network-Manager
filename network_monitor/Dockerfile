ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    python3 \
    py3-pip \
    iputils \
    net-tools \
    nmap \
    curl \
    jq

COPY rootfs/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY rootfs/app/ /app/app/
COPY rootfs/main.py /app/main.py
COPY rootfs/static/ /app/static/
COPY rootfs/etc/ /etc/

RUN chmod +x /etc/s6-overlay/s6-rc.d/network-monitor/run
