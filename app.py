#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmallParserService

Flask web service to run the SmallParser application from GCP as a REST service
"""

from pathlib import Path

from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

from tlparser import main as parse_timelog

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./uploads"
ALLOWED_EXTENSIONS = {'txt'}

@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    """Upload a file to the server."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filepath = Path(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
            file.save(filepath)
            results = parse_timelog(filepath)
            return render_template("display_results.html", results=results)
    return render_template("file_upload.html")


@app.route('/parse_json_timelog', methods=['POST'])
def parse_json_timelog():
    """Parse timelog as JSON"""
    if request.method == 'POST':
        


def allowed_file(f: str) -> bool:
    """Check if file type is allowed."""
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(host="0.0.0.0")
