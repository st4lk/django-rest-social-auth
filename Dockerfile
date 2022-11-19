FROM python:3.10.4

RUN mkdir -p /opt/runtime/
ADD scripts/* /opt/runtime/

RUN useradd -ms /bin/bash appuser
USER appuser

ENTRYPOINT ["/opt/runtime/entrypoint.sh"]
