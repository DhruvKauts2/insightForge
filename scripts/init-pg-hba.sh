#!/bin/sh
# Allow password authentication from all hosts
echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pgdata/pg_hba.conf
