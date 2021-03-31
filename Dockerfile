FROM python:3.9-slim
# TODO: FLASK_ENV shouldn't be hardcoded
ENV FLASK_APP="app.py" FLASK_ENV="development"
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN pipenv install --system --deploy
COPY . .
EXPOSE 5000
CMD [ "python", "app.py" ]
