FROM python:3.10-slim
ENV PYTHONPATH=/usr/src/app
WORKDIR ${PYTHONPATH}
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY ./server ./server
WORKDIR ./server
CMD ["python","main.py"]