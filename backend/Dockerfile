FROM python:3.9-bullseye
WORKDIR /usr/src/app

RUN python -m pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN apt-get install libpq-dev
RUN pip install -r requirements.txt
RUN pip install gunicorn
COPY . /usr/src/app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]