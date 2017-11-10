FROM python:3
WORKDIR /app
COPY requirements.txt /app
COPY oauth_creds.json /app
RUN pip3 install -r /app/requirements.txt
COPY ./multipong /app/multipong
CMD python3 -m multipong
