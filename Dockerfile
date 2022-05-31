# Base image
FROM python:3.10.4

RUN set -eux; \
    apt-get update; \
    apt-get install -y gosu; \
    rm -rf /var/lib/apt/lists/*; \
    # verify that the binary works
    gosu nobody true


RUN mkdir -p /opt/runtime/
ADD scripts/* /opt/runtime/

RUN useradd -ms /bin/bash appuser

ENTRYPOINT ["/opt/runtime/entrypoint.sh"]
