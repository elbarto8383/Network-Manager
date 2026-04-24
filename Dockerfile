ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.11
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    iputils \
    net-tools \
    curl

WORKDIR /app

COPY rootfs/app/ ./
COPY rootfs/requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY rootfs/run.sh /
RUN chmod a+x /run.sh

CMD ["/run.sh"]
