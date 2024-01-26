# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3

ARG DB_PASSWORD
ARG DB_USER
ARG DB_HOST
ARG DB_NAME

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

ENV POSTGRES_PASSWORD $DB_PASSWORD
ENV POSTGRES_DB $DB_NAME
ENV POSTGRES_USER $DB_USER
ENV POSTGRES_HOST $DB_HOST
ENV BACKEND_PORT 8080

# Install any needed packages specified in requirements.txt
# ENTRYPOINT ["python", "./manage.py"]
# CMD ["runserver", "0.0.0.0:${$BACKEND_PORT}"]

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

EXPOSE $BACKEND_PORT
CMD ["python", "manage.py", "runserver", "0.0.0.0:${$BACKEND_PORT}"]
