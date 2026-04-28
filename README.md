## Before first use
1. Set `.env` files:
    - in `api/src/config/` (`example.env` provided)
    - in `ui/mglyph-web-vue/` (`example.env` provided)
2. Set PostgreSQL secrets in `docker_config/` (based on `docker_config_example/`)

## Docker container
```sh
docker-compose build
```

```sh
docker-compose up
```

nebo též jedním příkazem
```sh
docker-compose up --build
```

### pro debugging (hot reload)
```sh
docker-compose watch
```
nebo
```sh
docker compose up --build --watch
```

### pro změnu docker-compose souboru
```sh
docker compose -f <FILE> up --build
```

## Fast API

Available at: `http://localhost:8888` <br>
Docs at: `http://localhost:8888/docs`


## Vue
Dev available at: `http://localhost:5173/`

## Alembic migrations

Make sure all models are imported in `api/src/db/alembic-migrations/env.py` file.

For all commands enter the `api/src/config` folder.

Useful alembic commands:
- Autogenerate migration
    ```sh
    alembic revision --autogenerate -m "<SHORT_DESCRIPTION>"
    ```
- Apply migrations
    ```sh
    alembic upgrade head
    ```
- Revert all migrations
    ```sh
    alembic downgrade base
    ```
- Show current revision ID of the database
    ```sh
    alembic current
    ```
- Set the `alembic_version` table to a specific revision ID without actually running the migration scripts
    ```sh
    alembic stamp <REVISION_ID>
    ```
- Generate SQL for specific migration
    ```sh
    alembic upgrade <previous>:<current> --sql
    ```

# Note
Possible extensions are in the comments and are prepended with `EXTENSION:`

