# Exit if any command fails
set -e

# Check python type hints
mypy .

# Emit openapi specification from FastAPI
python ./emit_openapi.py > openapi.json

# Generate TypeScript interfaces and classes
npx openapi-generator-cli generate -i openapi.json -g typescript-fetch -o ../frontend/src/generated
