FROM python:3.8-slim
ENV FLASK_APP="app.py" FLASK_ENV="development"
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD [ "python", "app.py" ]
