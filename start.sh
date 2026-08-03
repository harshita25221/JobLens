#!/bin/bash
export HF_HOME="$PWD/backend/.hf_cache"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

cd backend
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 1 --timeout 120 app:app
