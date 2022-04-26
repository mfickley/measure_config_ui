import json
import pandas as pd
import numpy as np

def translate_initiative(data):
    initiatives = data['initiatives']
    initiativeFrame = pd.DataFrame()
    for initiative in initiatives:
        initiativeFrame = pd.concat([initiativeFrame,pd.json_normalize(initiative)])
    initiativeFrame.columns = initiativeFrame.columns.str.lower()
    initiativeFrame = pd.DataFrame(initiativeFrame,columns=['name','enabled','periodtype','payersupplied','displayorder'])
    return initiativeFrame

def translate_initiative_lob(data):
    initiatives = data['initiatives']
    lobFrame = pd.DataFrame()
    for initiative in initiatives:
        lobFrame = pd.concat([lobFrame,pd.json_normalize(initiative,'includedLobNames',meta=['name'])])
    lobFrame.columns = lobFrame.columns.str.lower()
    lobFrame.rename(columns={np.NAN:'lobname','name':'initiative'},inplace = True)
    lobFrame = pd.DataFrame(lobFrame,columns=['initiative','lobname'])
    return lobFrame

def translate_initiative_measure(data):
    initiatives = data['initiatives']
    measureFrame = pd.DataFrame()
    for initiative in initiatives:
        measureFrame = pd.concat([measureFrame,pd.json_normalize(initiative,'assignedMeasures',meta=['name'])])
    measureFrame.columns = measureFrame.columns.str.lower()
    measureFrame.rename(columns = {'name':'initiative'}, inplace = True)
    measureFrame["thresholddirection"] = measureFrame["thresholddirection"].astype(int)
    measureFrame = pd.DataFrame(measureFrame,columns=['initiative','measure','rate','threshold','thresholddirection','displayorder','displayname','displayshortname','displaydescription','enabled'])
    measureFrame.sort_values(by=['initiative','measure','rate'])
    return measureFrame

def translate_payer_supplied(data):
    return pd.json_normalize(data,record_path = 'payerSuppliedMeasureMap')

def translate_thresholds(data):
    initiatives = data['initiatives']
    threshFrame = pd.DataFrame()

    for initiative in initiatives:
        for measure in initiative['assignedMeasures']:
            try:
                threshFrame = pd.concat([threshFrame,pd.json_normalize(measure,'qualityScoreThresholds',meta=['measure','rate'])])
                threshFrame =  threshFrame.assign(initiative=initiative['name'])
            except(KeyError):
                pass

    threshFrame.columns = threshFrame.columns.str.lower()

    #explicitly set indexes so that we can concat things in a minute
    threshFrame = threshFrame.reset_index(drop = True)

    #exploding each list
    t_splits = pd.DataFrame(threshFrame['thresholds'].to_list(),columns = ['threshold1','threshold2','threshold3','threshold4'])
    f_splits = pd.DataFrame(threshFrame['factors'].to_list(),columns = ['factor0','factor1','factor2','factor3','factor4'])

    #concat exploded thresholds/factors back to main dataframe
    threshFrame = pd.concat([threshFrame,t_splits],axis=1)
    threshFrame = pd.concat([threshFrame,f_splits],axis=1)

    #dropping unnecessary columns
    threshFrame = threshFrame.drop(['thresholds','factors'],axis=1)

    return threshFrame

def translate_weights(data):

    initiatives = data['initiatives']
    weightFrame = pd.DataFrame()

    for initiative in initiatives:
        for measure in initiative['assignedMeasures']:
            try:
                weightFrame = pd.concat([weightFrame,pd.json_normalize(measure,'qualityScoreWeights',meta=['measure','rate'])])
                weightFrame =  weightFrame.assign(initiative=initiative['name'])
            except(KeyError):
                pass
    
    weightFrame.columns = weightFrame.columns.str.lower()

    weightFrame = pd.DataFrame(weightFrame,columns=['initiative','locationdisplayname','calendaryear','measure','rate','weight','baseline'])
    weightFrame.sort_values(by=['initiative','measure','rate','locationdisplayname','calendaryear'])
    return weightFrame


def main():
    with open(r'C:\Users\mike.fickley\venv\measure_config_ui\src\app\data\uploads\test.json') as f:
        data = json.loads(f.read())

    PAYERSUPPLIEDMEASUREMAP = translate_payer_supplied(data)
    INITIATIVE = translate_initiative(data)
    INITIATIVELOB = translate_initiative_lob(data)
    INITIATIVEMEASURE = translate_initiative_measure(data)
    QUALITYSCORETHRESHOLD = translate_thresholds(data)
    QUALITYSCOREWEIGHT = translate_weights(data)

if __name__ == "__main__":
    main()