FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["t_race_stats"]
