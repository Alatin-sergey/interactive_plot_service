#!\bin\bash
echo "Starting backend..."
uvicorn backend:app --port ${BACKEND_PORT} --host ${BACKEND_HOST}