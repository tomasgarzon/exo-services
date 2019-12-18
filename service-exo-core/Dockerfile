FROM alpine:3.10 AS service-exo-core

LABEL maintainer="Ernesto Serrano <ernesto@openexo.com>"

WORKDIR /projects/service-exo-core

ARG SOURCE_TAG

ENV PYTHONUNBUFFERED=1 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PIPENV_YES=1 \
    SERVICE_NAME=service-exo-core

# Adding just Pipfile (best with latest versions)
COPY Pipfile .

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements fil
RUN apk add --no-cache \
        python3 \
        pango \
        py3-cairo \
        py3-cffi \
        py3-gobject3 \
        py3-pillow \
        py3-lxml \
        py3-curl \
        py3-psycopg2 \
        postgresql-client \
        curl \
        libcrypto1.1 \
        py3-openssl \
        zip \
        ipython \
        gettext \
        libc-dev \
    && \
        apk add --no-cache --virtual .build-deps  \
            git \
            build-base \
            python3-dev \
            libffi-dev \
            postgresql-dev \
            libxml2-dev \
            libxslt-dev \
            jpeg-dev \
            pango-dev \
            curl-dev \
    && \
        pip3 install pipenv \
    && \
        pip3 install "django<3.0" \
    && \
        pipenv install --system --skip-lock \
    && \
        apk del .build-deps --force-broken-world \
    && \
        find /usr/local -depth \
            \( \
                \( -type d -a \( -name test -o -name tests \) \) \
                -o \
                \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
            \) -exec rm -rf '{}' + \
        && rm -rf /usr/src/python \
        && rm -rf /root/.cache

# Show package versions
RUN pip3 freeze

# Copying rest of files
COPY . .

# Creating fake dirs for components
RUN mkdir -p exo-backoffice && \
    touch exo-backoffice/__init__.py

# Running basic check of django
RUN python3 manage.py check

EXPOSE 8000

CMD sh -f run.sh

ARG SOURCE_TAG

ARG SOURCE_BRANCH
ARG SOURCE_NAME
ARG AWS_KEY
ARG AWS_SECRET

ENV SOURCE_NAME=$SOURCE_NAME \
    SOURCE_BRANCH=${SOURCE_BRANCH} \
    SOURCE_TAG=${SOURCE_TAG} \
    AWS_KEY=${AWS_KEY} \
    AWS_SECRET=${AWS_SECRET} \
    REDIS_HOST=redis \
    DB_NAME=service_exo_core \
    DB_USER=exolever \
    DB_PASS=exolever \
    DB_HOST=postgres

# Check container healthy (disabled temparily)
#HEALTHCHECK --interval=5m --start-period=1m CMD curl -f http://localhost/ || exit 1
