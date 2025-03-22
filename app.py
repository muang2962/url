from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import string
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'muel2962hamhyunhighschool'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

def base36encode(number):
    chars = string.digits + string.ascii_uppercase
    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = chars[i] + base36
    return base36 or '0'

def generate_random_code(length=8):
    chars = string.digits + string.ascii_uppercase
    return ''.join(random.choice(chars) for _ in range(length))

def is_valid_url(url):
    try:
        result = urlparse(url)
        return result.scheme in ['http', 'https'] and result.netloc
    except Exception:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form.get('url', '').strip()

        if not original_url or not is_valid_url(original_url):
            flash("올바른 URL을 입력하세요.", "error")
            return render_template("index.html")

        existing_url = URL.query.filter_by(original_url=original_url).first()
        if existing_url:
            short_url = request.host_url + existing_url.short_code
            return render_template("result.html", short_url=short_url)

        new_url = URL(original_url=original_url)
        db.session.add(new_url)
        db.session.commit()

        new_url.short_code = generate_random_code()
        db.session.commit()

        short_url = request.host_url + new_url.short_code
        return render_template("result.html", short_url=short_url)

    return render_template("index.html")

@app.route('/<short_code>')
def redirect_short_url(short_code):
    url_data = URL.query.filter_by(short_code=short_code).first()
    if url_data:
        return redirect(url_data.original_url)
    return "URL Not Found", 404

if __name__ == '__main__':
    app.run(debug=True)