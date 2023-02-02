FROM python:3.10-slim

ENV PYTHONPATH=/usr/src/app
WORKDIR ${PYTHONPATH}

RUN apt-get update && apt install -y netcat

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY migrations ./migrations
COPY alembic.ini ./
COPY srv ./srv

ENTRYPOINT ["srv/entrypoint.sh"]
CMD ["python","srv/main.py"]