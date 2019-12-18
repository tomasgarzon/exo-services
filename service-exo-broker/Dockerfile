FROM alpine:3.10 as service-exo-broker

LABEL maintainer="Ernesto Serrano <ernesto@openexo.com>"
LABEL vendor="openexo"

WORKDIR /projects/service-exo-broker

ARG SOURCE_NAME

ENV SOURCE_NAME=$SOURCE_NAME

ENV PYTHONUNBUFFERED=1 \
    LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    PIPENV_YES=1 \
    SERVICE_NAME=service-exo-broker

# Adding just Pipfile (best with latest versions)
COPY Pipfile .

# Installing alpine base packages
RUN apk add --no-cache \
        curl \
        python3 \
        py3-openssl \
        py3-cffi \
        py3-cryptography \
        py3-requests \
        hiredis \
        nginx \
        ipython \
        gettext \
    && \
    apk add --no-cache --virtual .build-deps  \
        build-base \
        python3-dev \
        libffi-dev \
        linux-headers \
        git \
    && \
    pip3 install pipenv \
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


# # Check packages, when them fix this https://github.com/pypa/pipenv/issues/2783
# RUN pipenv check --system

# Show package versions
RUN pip3 freeze

# Copying rest of files
COPY . .

RUN sed -i "s/<SOURCE_NAME>/$SOURCE_NAME/" nginx.conf

# Copy NGINX error pages to default location
RUN ln -sf /projects/service-exo-broker/500.html /var/lib/nginx/html/500.html
RUN ln -sf /projects/service-exo-broker/50x.html /var/lib/nginx/html/50x.html

EXPOSE 8000
EXPOSE 8001

CMD sh -f run.sh


ARG SOURCE_BRANCH
ARG SOURCE_TAG

ENV SOURCE_BRANCH=${SOURCE_BRANCH} \
    SOURCE_TAG=${SOURCE_TAG}
