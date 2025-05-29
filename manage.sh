#!/bin/bash

# Load environment variables from .env
set -a
source .env
set +a

DOCKER_COMPOSE_FILE="docker-compose.yml"

function start_app() {
    echo "📦 Building and starting Docker services..."
    docker compose --env-file .env -f "$DOCKER_COMPOSE_FILE" up --build -d
    echo "🚀 App is running. Streamlit UI: http://localhost:8501"
}

function stop_app() {
    echo "🛑 Stopping and cleaning up Docker services..."
    docker compose --env-file .env -f "$DOCKER_COMPOSE_FILE" down -v
    echo "✅ Stopped and cleaned."
}

function status_app() {
    echo "📊 Docker container status:"
    docker compose --env-file .env -f "$DOCKER_COMPOSE_FILE" ps
}

function logs_app() {
    echo "📜 Streaming logs (Press Ctrl+C to stop):"
    docker compose --env-file .env -f "$DOCKER_COMPOSE_FILE" logs -f
}

case "$1" in
    --start)
        start_app
        ;;
    --stop)
        stop_app
        ;;
    --status)
        status_app
        ;;
    --logs)
        logs_app
        ;;
    *)
        echo "Usage: $0 [--start | --stop | --status | --logs]"
        exit 1
        ;;
esac
