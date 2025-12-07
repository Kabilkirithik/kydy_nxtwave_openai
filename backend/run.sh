#!/bin/bash
# Simple script to run the backend server
# Run from project root: ./backend/run.sh
# Or run from backend directory: ./run.sh

if [ -f "app.py" ]; then
    # Running from backend directory
    uvicorn app:app --reload
else
    # Running from project root
    cd backend
    uvicorn app:app --reload
fi

