#!/usr/bin/env python

# """Module docstring."""

# Imports
import pandas as pd
import json

# Module Constants
CUSTOMER_ACRONYM = "CCF"

# Module "Global" Variables
global_variable_file = "file.txt"
schema = ""

# Module Functions and Classes
def main():
    df = pd.read_csv(
        r"./src/app/data/uploads/template.csv"
    )

    df['qst_calendarYear'] = df['qst_calendarYear'].fillna(0).astype(int)
    df['qsw_calendarYear'] = df['qsw_calendarYear'].fillna(0).astype(int)
    
    dict = {"initiatives": []}
    init_index = 0
    initiatives = df["initiativeName"].unique()
    
    for initiative in initiatives:
        # build list of measures for that initiative
        measureExtract = pd.DataFrame(df[df["initiativeName"] == initiative],columns=(["backendName","rate","threshold","thresholdDirection","displayName","displayShortName","displayDescription","qst_calendarYear", "qst_threshold1", "qst_threshold2", "qst_threshold3", "qst_threshold4","qst_factor0", "qst_factor1", "qst_factor2", "qst_factor3", "qst_factor4","qsw_calendarYear", "qsw_locationDisplayName", "qsw_weight", "qsw_baseline","lobName"]),).drop_duplicates().sort_values(by=["backendName", "rate"])

        ##parse out first level of json
        assignedMeasures = pd.DataFrame(measureExtract,columns=(["backendName","rate","threshold","thresholdDirection","displayName","displayShortName","displayDescription",]),).drop_duplicates().sort_values(by=["backendName", "rate"])
        
        #add measures and lobs to initiative list
        dict["initiatives"].append(
            {"name": initiative,"assignedMeasures": pd.DataFrame.to_dict(assignedMeasures, orient="records")
            ,"includedLobNames":list(measureExtract['lobName'].fillna('null').unique())})
        
        #go back through and add thresholds/weights
        measure_index = 0
        for measure in dict["initiatives"][init_index]['assignedMeasures']:
            
            #adding in multithreshold
            qualityScoreThresholdsList = []
            qs_df = pd.DataFrame(measureExtract[(measureExtract["backendName"] == measure['backendName']) & (measureExtract["rate"] == measure['rate'])]
                                 ,columns=(["qst_calendarYear", "qst_threshold1", "qst_threshold2", "qst_threshold3", "qst_threshold4","qst_factor0", "qst_factor1", "qst_factor2", "qst_factor3", "qst_factor4"])).drop_duplicates()
            
            for index,row in qs_df.iterrows():
                if row['qst_calendarYear'] > 0:
                    thresholds = list(row['qst_threshold1':'qst_threshold4'])
                    factors = list(row['qst_factor0':'qst_factor4'])

                    qualityScoreThresholdsList.append({"calendarYear":row['qst_calendarYear']
                                                       ,'thresholds':thresholds
                                                       ,'factors':factors})
            
            #adding in weights
            qualityScoreWeightsList = []
            qw_df = pd.DataFrame(measureExtract[(measureExtract["backendName"] == measure['backendName']) & (measureExtract["rate"] == measure['rate'])]
                                 ,columns=(["qsw_calendarYear", 
                                            "qsw_locationDisplayName", 
                                            "qsw_weight", 
                                            "qsw_baseline"])).drop_duplicates()
            
            for index,row in qw_df.iterrows():
                if row['qsw_calendarYear'] > 0:
                    qualityScoreWeightsList.append({"calendarYear":row['qsw_calendarYear'],
                                                    'locationDisplayName':row['qsw_locationDisplayName'],
                                                    'weight':row['qsw_weight'],
                                                    'baseline':row['qsw_baseline']})
        
            #ADD SCORES AND WEIGHTS TO MEASURE
            if len(qualityScoreThresholdsList) > 0:
                dict["initiatives"][init_index]['assignedMeasures'][measure_index]['qualityScoreThresholds'] = qualityScoreThresholdsList
            if len(qualityScoreWeightsList) > 0:
                dict["initiatives"][init_index]['assignedMeasures'][measure_index]['qualityScoreWeights'] = qualityScoreWeightsList
        
            measure_index += 1
        init_index+=1

    with open(
        "./ref/test.json", "w"
    ) as outputFile:
        # Writing data to a file
        outputFile.writelines(json.dumps(dict))

    print('Output written to ' + outputFile.name)

if __name__ == "__main__":
    main()