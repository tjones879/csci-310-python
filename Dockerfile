FROM python:3
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt
COPY ./multipong /app/multipong
WORKDIR multipong
CMD python3 -u -m web
