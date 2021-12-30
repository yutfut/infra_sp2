FROM python:3.7-slim

COPY . /app

WORKDIR /app

run source venv/bin/activate

RUN pip3 install -r /app/requirements.txt --no-cache-dir

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]