#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmallParserService

Flask web service to run the SmallParser application from GCP as a REST service
"""

import json
from pathlib import Path

from flask import Flask, flash, request, redirect, render_template, jsonify, make_response
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix

import tlparser as tlp


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
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
            f.save(filepath.absolute())
            with open(filepath.absolute()) as log:
                timelog = log.readlines()
            records, total = tlp.parse_log(timelog)
            stats = tlp.record_stats(records, total, filepath.name)
            results = tlp.format_output(stats)
            return render_template("display_results.html", results=results)
    return render_template("file_upload.html")


@app.route('/parse_timelog', methods=['GET', 'POST'])
def parse_timelog():
    """Parse timelog as JSON"""
    if request.method == 'POST':
        timelog = json.loads(request.json)
        records, total = tlp.parse_log(timelog['timelog'])
        stats = tlp.record_stats(records, total, timelog['filename'])
        results = {'output': tlp.format_output(stats)}
        return make_response(jsonify(results), 200)
    return render_template("index.html")


def allowed_file(f: str) -> bool:
    """Check if file type is allowed."""
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(host="0.0.0.0")
