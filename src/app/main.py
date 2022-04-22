import os
import pandas as pd

from flask import Flask, render_template, request
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
from Forms import newMeasureForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config.update(
    UPLOAD_FOLDER=os.path.join(basedir, "uploads"),
    DROPZONE_MAX_FILE_SIZE=1024,
    DROPZONE_TIMEOUT=5 * 60 * 1000,
    ENV="development",
)

dropzone = Dropzone(app)

df = pd.read_csv(r".\src\app\data\uploads\initiativemeasure.csv")


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


@app.route("/create")
def create():
    form = newMeasureForm()
    return render_template("newMeasureForm.html", title="this is a form", form=form)


@app.route("/edit")
def edit():
    return render_template(
        "edit.html", tables=[df.to_html(classes="data")], titles=df.columns.values
    )


if __name__ == "__main__":
    app.run(debug=True)
