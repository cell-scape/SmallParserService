"""
SmallParserService.

Flask web service to run the SmallParser application from GCP.
"""

import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

from tlparser import main as parse_timelog

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = {'txt'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """Upload a file to the server."""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            results = parse_timelog(filepath)
            return render_template("display_results.html", results=results)
    return render_template("file_upload.html")


def allowed_file(f: str) -> bool:
    """Check if file type is allowed."""
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    app.run(host="0.0.0.0")
