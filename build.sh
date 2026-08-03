#!/bin/bash
set -e

echo "=== Setting up environment ==="
export HF_HOME="$PWD/backend/.hf_cache"

echo "=== Building Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Installing Backend Dependencies ==="
cd backend
pip install -r requirements.txt


echo "=== Build Complete ==="
