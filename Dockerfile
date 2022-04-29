FROM python:3.6

COPY manage.py gunicorn-cfg.py requirements.txt ./
COPY core core
COPY exploration exploration

RUN pip install -r requirements.txt
RUN mkdir logs
RUN touch logs/dashboard.log

EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
