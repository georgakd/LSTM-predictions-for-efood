FROM python:3.8

COPY manage.py gunicorn-cfg.py requirements.txt ./
COPY core core
COPY exploration exploration
COPY datasets datasets

COPY model_order_id.h5 ./
COPY model_total_order_value.h5 ./

RUN pip install -r requirements.txt
RUN mkdir logs
RUN touch logs/dashboard.log

RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
