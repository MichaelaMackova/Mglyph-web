FROM python:3.13-slim

# USER root

# Set up the working directory:
WORKDIR /code

# Update package lists and install dependencies needed to build psycopg2
# libpq-dev: PostgreSQL C library development files
# gcc: C compiler
RUN apt-get update && apt-get install -y libpq-dev gcc
# RUN apt-get update -y && apt-get install -y libgl1 ffmpeg

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


COPY ./src /code/src
EXPOSE 8888


# Copy wait-for-it script to wait for the database to be ready before starting the application
COPY ./wait-for-it.sh /code/wait-for-it.sh
RUN ["chmod", "+x", "/code/wait-for-it.sh"]

# Copy script to apply Alembic migrations
COPY ./upgrade_all_db_migrations.sh /code/upgrade_all_db_migrations.sh
RUN ["chmod", "+x", "/code/upgrade_all_db_migrations.sh"]


# Wait for the database to be ready and apply Alembic migrations before starting the application, with a timeout of 30 seconds for the database to become available
ENTRYPOINT ["./wait-for-it.sh", "-t", "30", "-s", "db:5432", "--", "./upgrade_all_db_migrations.sh"]

CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8888"]
