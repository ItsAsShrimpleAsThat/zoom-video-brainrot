import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def test():
  return "test"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6814)