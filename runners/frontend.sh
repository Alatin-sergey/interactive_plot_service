#!/bin/bash

echo "Starting frontend..."
streamlit run app.py --server.port ${FRONTEND_PORT}