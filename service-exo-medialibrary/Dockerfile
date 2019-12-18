FROM alpine:3.10 as service-exo-medialibrary

LABEL maintainer="Ernesto Serrano <ernesto@openexo.com>"
LABEL vendor="openexo"

WORKDIR /projects/service-exo-medialibrary

ENV PYTHONUNBUFFERED=1 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PIPENV_YES=1 \
    SERVICE_NAME=service-exo-medialibrary

# Adding just Pipfile to  optimize docker layer cache build
COPY Pipfile .

# Installing alpine base packages
RUN apk add --no-cache \
        curl \
        python3 \
        py3-openssl \
        py3-cffi \
        py3-cryptography \
        py3-requests \
        py3-psycopg2 \
        py3-service_identity \
        py3-attrs \
        postgresql-client \
        postgresql-dev \
        ipython \
        gettext \
        libc-dev \
    && \
    apk add --no-cache --virtual .build-deps  \
        build-base \
        python3-dev \
        libffi-dev \
        git \
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

# Check packages #TODO when this bug will be fixed https://github.com/pypa/pipenv/issues/2783
# RUN pipenv check --system

# Show package versions
RUN pip3 freeze

# Copying rest of files
COPY . .

# Running basic check of django
RUN python3 manage.py check

EXPOSE 8000

CMD sh -f run.sh

# Check container healthy
# HEALTHCHECK --interval=5m --start-period=1m CMD curl -f http://localhost:8000/ || exit 1

ARG SOURCE_BRANCH
ARG SOURCE_TAG
ARG SOURCE_NAME

ENV SOURCE_NAME=$SOURCE_NAME \
    SOURCE_BRANCH=${SOURCE_BRANCH} \
    SOURCE_TAG=${SOURCE_TAG} \
    PYTHONUNBUFFERED=1 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PIPENV_YES=1 \
    PIPENV_NOSPIN=true \
    DB_NAME=service_exo_medialibrary \
    DB_USER=exolever \
    DB_PASS=exolever \
    DB_HOST=postgres \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    VIMEO_TOKEN=540ca8a178c5886adcef9b8b87a1b4b6 \
    VIMEO_CLIENT_ID=22124d0fd1956a2eadfa8cfedaa646683a41aa26 \
    VIMEO_CLIENT_SECRET="86IF4reGKn8vvu4BmlC/GRwsxQRhnwOF6UQWeCvYe++iB8HNIP/B0b3DJtmkwbikVAFVQB+KExK/Fwe+Dd/V063nue5jGAC0aM1AF4ftl9sPP8Bga/PFMdkq402rnRDz" \
    YOUTUBE_API_KEY=AIzaSyCnhi5jTAYiE8tVq91399422GvbxFS8H3Y \
    FILESTACK_KEY=AvvsSOUhSNGp7ybufZ6lbz
