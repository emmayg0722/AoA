FROM python:3.12-slim
WORKDIR /app/use-case-discovery-board
COPY relay.py github_store.py ./
EXPOSE 4317
CMD ["python3", "relay.py", "--host", "0.0.0.0", "--allow-origin", "https://emmayg0722.github.io"]
