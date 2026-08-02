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

echo "=== Downloading ML Models for caching ==="
# This ensures the model is downloaded during the build phase
# so it doesn't cause a timeout during runtime!
python -c "from keybert import KeyBERT; KeyBERT()"
echo "=== Build Complete ==="
