#!/bin/bash

set -eu
cd $(dirname $0)

. ../db.env

PG_CONTAINER=pgserv
docker exec -it $PG_CONTAINER psql -U $POSTGRES_USER $POSTGRES_DB \
     --file /drop-db-data.sql
