ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    iputils \
    net-tools \
    nmap \
    curl \
    jq

COPY rootfs/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY rootfs/ /app/

RUN chmod +x /app/run.sh

WORKDIR /app

CMD ["/app/run.sh"]
