import os

from flask import Flask, render_template, request
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER=os.path.join(basedir, "uploads"),
    DROPZONE_MAX_FILE_SIZE=1024,
    DROPZONE_TIMEOUT=5 * 60 * 1000,
    ENV="development",
)

dropzone = Dropzone(app)


@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        if request.files.get("file"):
            f = request.files.get("file")
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], f.filename))
        elif request.form.get("action1"):
            pass
        else:
            pass
    # elif request.method == 'GET':
    #     return render_template('contact.html')
    return render_template("upload.html")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)
