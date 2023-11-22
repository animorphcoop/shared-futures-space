#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: ./backup-database.sh

This script dumps the shared futures database in Postgres custom format'
    exit
fi

cd "$(dirname "$0")"

main() {
    pg_dump -Fc --no-acl sfs_db -h localhost -U sfs_user -f /home/deploy/backups/sfs-"$(date --utc +%Y%m%d-%H%M%S)".dump -w

    # to restore:
    # pg_restore -v -h localhost -cO --if-exists -d sfs_db -U sfs_user -W sfs-xxx.dump

    # delete dumps older than 7 days
    find /home/deploy/backups -name "sfs-*.dump" -type f -mtime +7 -delete
}

main "$@"
