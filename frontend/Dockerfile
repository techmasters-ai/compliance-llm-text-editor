FROM python:3.11-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_HEADLESS=true

CMD ["sh", "-c", "streamlit run main.py --server.port=${FRONTEND_PORT:-8501} --server.address=0.0.0.0"]



