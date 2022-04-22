from flask_wtf import FlaskForm
from flask import request
from wtforms import SubmitField, StringField, validators, SelectField
import pandas as pd
# import requests

COMBOS = pd.read_csv(r"./src/app/data/appdata/airtable_measure_rates.csv")
MEASURES = COMBOS["Backend Name"].values
MEASURES.sort()
RATES = COMBOS["Backend Rate"].drop_duplicates()
RATES = RATES.values
RATES.sort()



class newMeasureForm(FlaskForm):
    initiative = StringField("Initiative Name", [validators.Length(min=1, max=50)])
    specOwner = SelectField(
        label="Spec Owner", choices=["HEDIS", "CMS ACO", "ARIZONA MEDICAID"]
    )
    backendName = SelectField(label="Backend Name", choices=MEASURES)
    rate = SelectField("Rate", choices=RATES)
    threshold = StringField("Threshold", [validators.number_range(0, 1)])
    shortname = StringField("Short Name", [validators.Length(min=0, max=10)])
    description = StringField("Description", [validators.Length(min=6, max=35)])
    submit = SubmitField("Create Measure Artifacts")

if __name__ == "__main__":
    print(COMBOS)
    print(MEASURES)
    print(RATES)
