#!/bin/bash
set -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv global 3.12.14

cd /home/frappe

if [ ! -d "/home/frappe/frappe-bench/apps/frappe" ]; then
    echo "=== 1. Initializing Frappe Bench (v15) ==="
    bench init \
        --ignore-exist \
        --skip-redis-config-generation \
        --frappe-branch version-15 \
        --python $(pyenv which python) \
        /home/frappe/frappe-bench
fi

cd /home/frappe/frappe-bench

echo "=== 2. Setting common site config ==="
bench set-config -g db_host mariadb
bench set-config -g redis_cache redis://redis-cache:6379
bench set-config -g redis_queue redis://redis-queue:6379
bench set-config -g redis_socketio redis://redis-queue:6379

echo "=== 3. Creating site coding.localhost ==="
if [ ! -d "/home/frappe/frappe-bench/sites/coding.localhost" ]; then
    bench new-site coding.localhost \
        --admin-password admin \
        --mariadb-root-password 123 \
        --no-mariadb-socket
fi

echo "=== 4. Fetching and installing LMS app ==="
if [ ! -d "/home/frappe/frappe-bench/apps/lms" ]; then
    bench get-app lms --branch version-15
fi
bench --site coding.localhost install-app lms || true

echo "=== 5. Linking and installing coding_lms app ==="
if [ ! -d "/home/frappe/frappe-bench/apps/coding_lms" ]; then
    bench get-app /workspace/coding_lms_app
fi
bench --site coding.localhost install-app coding_lms || true

echo "=== 6. Running migrate ==="
bench --site coding.localhost migrate

echo "=== SUCCESS: Frappe LMS + coding_lms Ready! ==="
