#!\bin\bash
echo "Starting backend..."
uvicorn backend:app --port ${BACKEND_PORT} --host 0.0.0.0