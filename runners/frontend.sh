#!/bin/bash

echo "Starting frontend..."
streamlit run app.py --server.port ${FRONTEND_PORT} --server.address ${FRONTEND_HOST}