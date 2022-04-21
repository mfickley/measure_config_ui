#!/usr/bin/env python

# """Module docstring."""

# Imports
import pandas as pd
import json
import argparse
import time

#argparse parameters
parser = argparse.ArgumentParser(description = 'Reads in a measure config file and returns all required formats')
parser.add_argument('--flatfile',action='store_true',help='sets all dataframes based on a single file instead of multiple components')
parser.add_argument('--measurePackage',action='store_true',help='exports a formatted measure package as well')
parser.add_argument('--outputoverride',help='file to output to')
parser.add_argument('--inputoverride',help='file to input !!!THIS ONLY WORKS IF --flatfile IS ALSO ENABLED!!!')
args = parser.parse_args()

# Module Constants
# CUSTOMER_ACRONYM = "ccf"
# NAMESPACE = 'uat'
# INFRASTRUCTURE = 'installation2'
if args.outputoverride is None:
    OUTPUT_PATH = f'./src/app/data/output/measure_ui_config_{time.strftime("%Y%m%d-%H%M%S")}.json'
else:
    OUTPUT_PATH = args.outputoverride

if args.inputoverride is None:
    INPUT_PATH = r'./src/app/data/uploads/qdw_export.csv'
else:
    INPUT_PATH = args.inputoverride
    

# Module "Global" Variables
if args.flatfile == False:
    print("Loading from multi-file source...")
    initiativeFrame = pd.read_csv(r"./src/app/data/uploads/initiative.csv")
    measureFrame = pd.read_csv(r"./src/app/data/uploads/initiativemeasure.csv")
    lobFrame = pd.read_csv(r"./src/app/data/uploads/initiativelob.csv")
    thresholdFrame = pd.read_csv(r"./src/app/data/uploads/qualityscorethreshold.csv")
    weightFrame = pd.read_csv(r"./src/app/data/uploads/qualityscoreweight.csv")
    payerSuppliedFrame = pd.read_csv(r"./src/app/data/uploads/payersuppliedmeasuremap.csv",dtype={'sourcepartition':str})

if args.flatfile == True:
    print("Loading from flat file source...")
    flat = pd.read_csv(INPUT_PATH,dtype={'sourcepartition':str})
    measureFrame = pd.DataFrame(flat,columns=['initiative','measure','rate','threshold','thresholddirection','displayname','displaydescription','displayshortname']).drop_duplicates().dropna()
    lobFrame = pd.DataFrame(flat,columns=['initiative','lobname']).drop_duplicates().dropna(thresh=1)
    thresholdFrame = pd.DataFrame(flat,columns=['initiative','measure','rate','qst_calendaryear','threshold1','threshold2','threshold3','threshold4','factor0','factor1','factor2','factor3','factor4']).drop_duplicates().dropna()
    weightFrame = pd.DataFrame(flat,columns=['initiative','measure','rate','qsw_calendaryear','locationdisplayname','weight','baseline']).drop_duplicates().dropna()
    payerSuppliedFrame = pd.DataFrame(flat,columns=['sourcepartition','payersuppliedname','arcadianame','arcadiarate']).drop_duplicates().dropna()

#update column names to fit json schema

measureFrame = measureFrame.rename(columns={
    "thresholddirection":"thresholdDirection"
    ,'displayorder':'displayOrder'
    ,'displayname':'displayName'
    ,'displayshortname':'displayShortName'
    ,'displaydescription':'displayDescription'})

thresholdFrame = thresholdFrame.rename(columns={
    "calendaryear":"calendarYear"
    ,'qst_calendaryear':'calendarYear'})

weightFrame = weightFrame.rename(columns={
    "calendaryear":"calendarYear"
    ,'locationdisplayname':'locationDisplayName'
    ,'qsw_calendaryear':'calendarYear'
})

payerSuppliedFrame = payerSuppliedFrame.rename(columns={
'sourcepartition':'payerSource',
'payersuppliedname':'payerMeasureName'
,'arcadianame':'arcadiaMeasureName'
,'arcadiarate':'arcadiaMeasureRate'
})

# Module Functions and Classes
def assignedMeasureList(initiative):
    df = pd.DataFrame(measureFrame[
        (measureFrame["initiative"] == initiative)]
        ,columns=(['measure','rate','threshold','thresholdDirection','displayName','displayDescription','displayShortName'])).drop_duplicates()

    #df = df.rename(columns={"backendName":"measure"})
    df['thresholdDirection'] = df['thresholdDirection'].astype(bool)
    measureList = pd.DataFrame.to_dict(df, orient="records")

    for measure in measureList:
        thresholds = thresholdList(initiative,measure['measure'],measure['rate'])
        weights = weightList(initiative,measure['measure'],measure['rate'])

        if len(thresholds) > 0:
            measure['qualityScoreThresholds'] = thresholds
        if len(weights) > 0:
            measure['qualityScoreWeights'] = weights
    
    return measureList

def thresholdList(initiative,measure,rate):
    output = []
    df = pd.DataFrame(thresholdFrame[
        (thresholdFrame["initiative"] == initiative) &
        (thresholdFrame["measure"] == measure) & 
        (thresholdFrame["rate"] == rate)]
        ,columns=(["calendarYear"
                , "threshold1"
                , "threshold2"
                , "threshold3"
                , "threshold4"
                , "factor0"
                , "factor1"
                , "factor2"
                , "factor3"
                , "factor4"])).drop_duplicates()

    df = df.astype({'calendarYear':int})

    for index,row in df.iterrows():
        if row['calendarYear'] > 0:
            thresholds = list(row['threshold1':'threshold4'])
            factors = list(row['factor0':'factor4'])
            output.append({"calendarYear":row['calendarYear']
                                                ,'thresholds':thresholds
                                                ,'factors':factors})
    return output

def weightList(initiative,measure,rate):
    output = []
    #adding in weights
    df = pd.DataFrame(weightFrame[
        (weightFrame["initiative"] == initiative) & 
        (weightFrame["measure"] == measure) & 
        (weightFrame["rate"] == rate)]
        ,columns=(["calendarYear", 
                "locationDisplayName", 
                "weight", 
                "baseline"])).drop_duplicates()

    df = df.astype({'calendarYear':int,'baseline':int})

    for index,row in df.iterrows():
        if row['calendarYear'] > 0:
            output.append({"calendarYear":row['calendarYear'],
                                            'locationDisplayName':row['locationDisplayName'],
                                            'weight':row['weight'],
                                            'baseline':row['baseline']})
    return output

def main():
    #declare initiatives
    dict = {"initiatives": []}
    initiatives = measureFrame["initiative"].unique()

    #iterate through initiatives and add assigned measures
    for initiative in initiatives:
        dict['initiatives'].append(
            {
            "name": initiative,
            "assignedMeasures": assignedMeasureList(initiative),
            "includedLobNames": list(lobFrame['lobname'].fillna('null').unique())
            }
        )

    #add in payerSupplied data if it exists
    if not payerSuppliedFrame.empty:
        dict['payerSuppliedMeasureMap'] = pd.DataFrame.to_dict(payerSuppliedFrame, orient="records")
        
    #write out
    with open(OUTPUT_PATH, "w") as outputFile:
        outputFile.writelines(json.dumps(dict))
        print('Measure UI Config written to ' + outputFile.name)

    if args.measurePackage == True:

        pkg = pd.DataFrame(measureFrame,columns=['measure','rate']).drop_duplicates().dropna()
        ae = pd.read_csv(r"./src/app/data/appdata/airtable_measure_rates.csv")
        ae = ae.rename(columns={"Backend Name":"measure",'Backend Rate':'rate','V6 Function Name':'script'})

        df = pd.merge(pkg,ae,on=['measure','rate'])

        dict = {
                    "@type": "MeasureConfig",
                    "properties": {
                        "batchJobScale": "db.r5.8xlarge",
                        "eligibilityLagMonths": 2
                    },
                    "calendarYears": 2,
                    "trailingYears": 2,
                    "measures": []
                }
        
        for index,measure in df.iterrows():
            dict['measures'].append([measure['script'],measure['rate']])

        with open(f'./src/app/data/output/measure_pkg_config_{time.strftime("%Y%m%d-%H%M%S")}.json', "w") as outputFile:
            outputFile.writelines(json.dumps(dict))
            print('Measure Package written to ' + outputFile.name)

if __name__ == "__main__":
    main()
