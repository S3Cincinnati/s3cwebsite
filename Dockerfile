FROM python:3.9-buster

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
RUN python3 manage.py collectstatic --clear --no-post-process --noinput

# EXPOSE 8000


CMD gunicorn --bind 0.0.0.0:$PORT s3cwebsite.wsgi