FROM python:slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app app
COPY simple_forum.py config.py entrypoint.sh ./
RUN chmod a+x entrypoint.sh

ENV FLASK_APP=simple_forum.py

EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]