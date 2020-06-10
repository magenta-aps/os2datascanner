# Copyright (C) 2020 Magenta ApS, http://magenta.dk.
# Contact: info@magenta.dk.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

################################################################################
# Changes to this file requires approval from Labs. Please add a person from   #
# Labs as required approval to your MR if you have any changes.                #
################################################################################

FROM node:14 AS frontend

WORKDIR /code/src/os2datascanner/projects/admin/adminapp

COPY src/os2datascanner/projects/admin/adminapp/package.json .
# TODO: use a lock-file and change to using npm ci (https://docs.npmjs.com/cli/ci#description)
RUN npm install

COPY src/os2datascanner/projects/admin/adminapp/postcss.config.js .
COPY src/os2datascanner/projects/admin/adminapp/webpack.dev.js .
COPY src/os2datascanner/projects/admin/adminapp/webpack.prod.js .
COPY src/os2datascanner/projects/admin/adminapp/static/src ./static/src
COPY src/os2datascanner/projects/admin/adminapp/static/3rdparty ./static/3rdparty
# Do we need templates?

# Build production bundle
# NB! Doesn't start a webserver, only bundles files!
RUN npm run prod

# Build development bundle
# NB! Watches for changes, so no automatic exit!
CMD ["npm", "run", "dev"]

######################

FROM python:3.6 AS application

LABEL org.opencontainers.image.title="OS2datascanner - Administration" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MPL-2.0" \
      org.opencontainers.image.url="https://os2datascanner.magenta.dk/" \
      org.opencontainers.image.documentation="https://os2datascanner.readthedocs.io/en/latest/" \
      org.opencontainers.image.source="https://github.com/os2datascanner/os2datascanner"

# Force the stdout and stderr streams from python to be unbuffered. See
# https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=1 \
  DSC_ADMIN_SYSTEM_CONFIG_PATH=/code/docker/docker-settings.toml \
  DSC_ADMIN_USER_CONFIG_PATH=/user-settings.toml \
  PYTHONPATH=/code/src/:$PYTHONPATH

# Ensure system user and install system depedencies
WORKDIR /code/requirements/sys-requirements
COPY requirements/sys-requirements/sys-requirements-common.txt \
     requirements/sys-requirements/sys-requirements-django.txt \
     requirements/sys-requirements/sys-requirements-admin.txt \
     ./
RUN cat sys-requirements-*.txt > sys-requirements.txt
RUN set -ex \
  # Add an application specific group and user.
  # Note: this is a system user/group, but have
  # UID/GID above the normal SYS_UID_MAX/SYS_GID_MAX of 999, but also above the
  # automatic ranges of UID_MAX/GID_MAX used by useradd/groupadd.
  # Hopefully there will be no conflicts with users of the
  # host system or users of other docker containers.
  && groupadd -g 73020 -r os2ds_admin\
  && useradd -u 73020 --no-log-init -r -g os2ds_admin os2ds_admin \
  # Install system dependencies from file.
  && apt-get -y update \
  && apt-get -y install --no-install-recommends $(grep -o '^[^#][[:alnum:].-]*' sys-requirements.txt) \
  # clean up after apt-get and man-pages
  && apt-get clean && rm -rf "/var/lib/apt/lists/*" "/tmp/*" "/var/tmp/*" "/usr/share/man/??" "/usr/share/man/??_*" \
  # create folders for output from django
  && install -o os2ds_admin -g os2ds_admin -d /code/build \
  && install -o os2ds_admin -g os2ds_admin -d /code/var

# Install python requirements
WORKDIR /code/requirements/python-requirements
COPY requirements/python-requirements/requirements-admin.txt \
     requirements/python-requirements/requirements-test.txt \
     requirements/python-requirements/requirements-lint.txt \
     ./
RUN pip install \
    -r requirements-admin.txt \
    -r requirements-test.txt \
    -r requirements-lint.txt

WORKDIR /code/docker/
COPY docker/admin .
COPY docker/docker-entrypoint-django.sh ./docker-entrypoint.sh

# Copy backend code
WORKDIR /code/src/os2datascanner
COPY src/os2datascanner/projects/admin ./projects/admin
COPY src/os2datascanner/projects/__init__.py ./projects/
COPY src/os2datascanner/tests ./tests
COPY src/os2datascanner/utils ./utils
COPY src/os2datascanner/__init__.py ./
COPY VERSION .
COPY LICENSE .
COPY README .
COPY NEWS.rst .
# Copy necessary files from engine module TODO: minimize this
COPY src/os2datascanner/engine2 ./engine2

# Copy frontend code
WORKDIR /code/src/os2datascanner/projects/admin/adminapp/static/dist
COPY --from=frontend /code/src/os2datascanner/projects/admin/adminapp/static/dist/bundle.min.js .
COPY --from=frontend /code/src/os2datascanner/projects/admin/adminapp/static/dist/bundle.min.css .

# Run the server as the os2ds_admin user on port 8000
WORKDIR /code/src/os2datascanner/projects/admin
USER os2ds_admin:os2ds_admin
EXPOSE 8000
ENTRYPOINT ["/code/docker/docker-entrypoint.sh"]
CMD ["django-admin", "shell"]