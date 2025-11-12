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
CMD ["fastapi", "run", "src/main.py", "--host", "0.0.0.0", "--port", "8888"]
