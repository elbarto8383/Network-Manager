ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    iputils \
    net-tools \
    curl \
    jq

WORKDIR /app

COPY rootfs/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY rootfs/ ./

RUN chmod a+x /app/run.sh

CMD ["/app/run.sh"]
