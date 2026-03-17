FROM docker.io/astral/uv:python3.12-alpine

# Install pylupdate5 and pylupdate6
# hadolint ignore=DL3018
RUN apk add --no-cache \
    py3-qt5 \
    py3-qt6 \
    bash \
    ca-certificates

WORKDIR /app
COPY . .

RUN uv tool install .

WORKDIR /workdir

ENTRYPOINT ["/usr/local/bin/qpdt"]
