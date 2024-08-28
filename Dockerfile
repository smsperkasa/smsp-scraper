FROM python:3.12.5

WORKDIR /home/smsp/smsp-scraper/

COPY . .
RUN pip install -r requirements.txt

# CMD python run.py
