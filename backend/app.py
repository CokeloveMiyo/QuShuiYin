from flask import Flask, render_template
from flask_cors import CORS
import os
from src.api import parse, download

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'qingying-dev-secret')
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.register_blueprint(parse.bp, url_prefix='/api')
app.register_blueprint(download.bp, url_prefix='/api')


@app.route('/')
def index():
    """API status page."""
    return render_template('landing.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8051, debug=True)
