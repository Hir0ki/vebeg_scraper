from python:3.8



RUN apt-get update

COPY ./poetry.lock  .
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml pyproject.toml
RUN poetry install --no-dev --no-root

ENV PYTHONPATH /
COPY logging.yml /logging.yml
COPY vebeg_scraper vebeg_scraper
COPY start.sh start.sh
CMD ./start.sh