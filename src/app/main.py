import os
import pandas as pd

from flask import Flask, render_template, request
from flask_dropzone import Dropzone
from werkzeug.utils import secure_filename
from Forms import newMeasureForm, envSelect
from mypkg.flatten_json import *

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

with open(
    r"C:\Users\mike.fickley\venv\measure_config_ui\src\app\data\uploads\test.json"
) as f:
    data = json.loads(f.read())

init = translate_initiative(data)
lob = translate_initiative_lob(data)
meas = translate_initiative_measure(data)
psm = translate_payer_supplied(data)
qst = translate_thresholds(data)
qsw = translate_weights(data)


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


@app.route("/test/", methods=["POST", "GET"])
def test():
    if request.method == "GET":
        return "test"
    if request.method == "POST":
        return "test2"


@app.route("/create", methods=["POST", "GET"])
def create():
    form = newMeasureForm()
    if request.method == "POST" and form.validate():
        return form.initiative.data
    else:
        return render_template("newMeasureForm.html", title="this is a form", form=form)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = envSelect()
    if envSelect().validate_on_submit():
        # return f's3://{form.customer.data.lower()}.objectstore.installation2.arcadia/{form.environment.data.lower()}/configuration/measure-ui.json'
        return render_template(
            "edit.html",
            tables=[
                init.to_html(index=False, justify="left", classes="data"),
                lob.to_html(index=False, justify="left", classes="data"),
                meas.to_html(index=False, justify="left", classes="data"),
                psm.to_html(index=False, justify="left", classes="data"),
                qst.to_html(index=False, justify="left", classes="data"),
                qsw.to_html(index=False, justify="left", classes="data"),
            ],
            titles=[
                "",
                "Initiatives",
                "LOB Mapping",
                "Measures",
                "PayerSupplied",
                "Thresholds",
                "Weights",
            ],
            form=form,
        )

    return render_template("edit.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)
