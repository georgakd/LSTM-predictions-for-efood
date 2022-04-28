FROM python:3.6

COPY manage.py gunicorn-cfg.py requirements.txt ./
COPY core core

RUN pip install -r requirements.txt

COPY cron_3.0pl1-137_amd64.deb ./
RUN dpkg -i cron_3.0pl1-137_amd64.deb

RUN mkdir logs
RUN touch logs/dashboard.log

EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
