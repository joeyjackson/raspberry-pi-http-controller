FROM python:alpine
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ENV FLASK_APP=app
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]