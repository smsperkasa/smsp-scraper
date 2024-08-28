FROM python:3.12.5

RUN apt-get update
RUN apt-get install -y --no-install-recommends vim
WORKDIR /home/smsp/smsp-scraper/

COPY . .
RUN pip install -r requirements.txt

# CMD python run.py
