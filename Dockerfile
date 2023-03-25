##############################################
# write git info
##############################################
FROM alpine/git:v2.36.3 AS git

WORKDIR /app
COPY .git /app/.git/
RUN git describe --tags --always > /git-describe
RUN git rev-parse HEAD > /git-commit
RUN date +'%Y-%m-%d %H:%M %Z' > /build-date



##############################################
# Main image
##############################################
FROM python:3.11.2-slim-bullseye AS final

ARG DEBIAN_FRONTEND=noninteractive

# Setup user & group
##############################################
RUN groupadd -g 1000 django
RUN useradd -M -d /app -u 1000 -g 1000 -s /bin/bash django

# Setup system
##############################################
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        libxml2 \
        media-types

# Fetch project requirements
##############################################
COPY --chown=django:django --from=git /git-describe /git-commit /build-date /app/git/

# Create directory structure
##############################################
WORKDIR /app
COPY --chown=django:django pyproject.toml requirements.txt ./
ADD --chown=django:django ./src ./src
COPY --chown=django:django tasks.py ./tasks.py

RUN mkdir -p /app/data /app/db
RUN chown django:django /app /app/data /app/db

ENV STATIC_ROOT=/app/static
ENV SECRET_KEY "changeme"
ENV DEBUG "false"
ENV DB_BASE_DIR "/app/db"

RUN python -m pip install --no-cache-dir -r requirements.txt
WORKDIR /app/src
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

WORKDIR /app/src

HEALTHCHECK --start-period=30s CMD python -c "import requests; requests.get('http://localhost:8000', timeout=2)"

USER django
CMD ["gunicorn", "checkout.wsgi", "--graceful-timeout=5", "--worker-tmp-dir=/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "--bind=0.0.0.0:8000", "--log-file=-"]
