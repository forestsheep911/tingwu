FROM python:3.11-slim
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/
EXPOSE 9000
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "9000"]