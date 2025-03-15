FROM python:3.12

WORKDIR /api

COPY . /api/

RUN pip install -r /api/webapp/API/requirements.txt

EXPOSE 5000

CMD ["python", "/api/webapp/API/app.py"]
