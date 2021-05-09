from main import app
import json

print(json.dumps(app.openapi()))
