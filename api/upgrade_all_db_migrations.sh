#!/bin/sh
alembic --config ./src/config/alembic.ini upgrade head
exec "$@"