#!/usr/bin/env bash

# Important files that should not be overwritten:
# .secret, pika_settings, local_settings, service files.

# *Note: At the moment pipeline_collector uses var/debug.log as log file.
# It has not rotation enabled and will quickly fill up the system.
set -e

repo_dir="`dirname "$BASH_SOURCE[0]"`/../../../"


source "$repo_dir/contrib/system-scripts/production/.env"
source "$repo_dir/contrib/system-scripts/utils/common.sh"
echo "$PRODUCTION_DIR"

echo -e '\n************* Copy *************\n'
# Copy to prod dir
update_prod_dir "$PRODUCTION_DIR"

# Run installation
echo -e '\n************* Installation *************\n'
# Install system dependencies and python-env
source ""$PRODUCTION_DIR"/install.sh"

if [ "$INSTALL_WEB_PROJECTS" = true ]
then
    echo -e '\n************* Admin module *************\n'
    export OS2DS_ADMIN_USER_CONFIG_PATH="$PRODUCTION_DIR/contrib/config/admin-module/user-settings.toml"
    export OS2DS_ADMIN_SYSTEM_CONFIG_PATH=""
    # Make migrations
    perform_django_migrations 'admin' "$PRODUCTION_DIR"

    # Collect static & Make messages
    npm_install_and_build 'admin' "$PRODUCTION_DIR" 'prod'
    collectstatic_and_makemessages 'admin' "$PRODUCTION_DIR"

    echo -e '\n************* Report module *************\n'
    export OS2DS_REPORT_USER_CONFIG_PATH="$PRODUCTION_DIR/contrib/config/report-module/user-settings.toml"
    export OS2DS_REPORT_SYSTEM_CONFIG_PATH=""
    # Make migrations
    perform_django_migrations 'report' "$PRODUCTION_DIR"

    # Collect static & Make messages
    npm_install_and_build 'report' "$PRODUCTION_DIR" 'prod'
    collectstatic_and_makemessages 'report' "$PRODUCTION_DIR"
fi

sudo chown --recursive www-data:www-data "$PRODUCTION_DIR"

echo -e '\n************* Restarting os2ds-services *************\n'
# Restart os2ds-*
systemctl restart os2ds-*

echo -e '\n************* Restarting apache2 *************\n'
# Restart apache
systemctl restart apache2.service

echo -e '\n************* Success *************\n'

echo -e '\n************* Simple Verification *************\n'

systemctl status os2ds-*

systemctl status apache2.service
