# Docker Support

This project supports Docker-based execution for quick local setup and demo portability.

## Run with Docker

From the project root:

```bash
docker build -t email-declutter .
docker run -p 8501:8501 email-declutter
```
Then open in browser:
```bash
http://127.0.0.1:8501
```
## Run with Docker Compose

```bash
docker compose up --build
