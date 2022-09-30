FROM arm32v6/python:alpine
WORKDIR /app
RUN apk update && apk add python3-dev gcc libc-dev libffi-dev g++
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "app.py"]