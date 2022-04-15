#validate the data

#check it against either the schema or the field_specs.json doc in app/data/appdata/
#also check that the measure/rate combination is correct by crossreferencing app/data/appdata/airtable_measure_rates.csv
import pandas as pd

# Module "Global" Variables
airtable_extract = r"./src/app/data/appdata/airtable_measure_rates.csv"

def is_name_rate_valid(backendName,rate):
    df = pd.read_csv(airtable_extract)
    return not (df[(df["Backend Name"] == backendName) & (df["Backend Rate"] == rate)].empty)

if __name__ == "__main__":
    print(is_name_rate_valid(backendName='CMSACO2020PREV7',rate='Default')) #good
    print(is_name_rate_valid(backendName='CMSACO2020PEV7',rate='Default'))  #bad name
    print(is_name_rate_valid(backendName='CMSACO2020PEV7',rate='Defaultr')) #bad rate
    print(is_name_rate_valid(backendName='CMSACO2020PREV7',rate='Defaultr'))#both bad