#!/bin/bash

echo "========================================"
echo "   SquirRL-Auditor Web Application"
echo "========================================"
echo ""
echo "Starting Streamlit server..."
echo ""

cd "$(dirname "$0")"
streamlit run app/main.py --server.port 8501



