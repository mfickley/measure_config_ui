/***************************************************************************************************
Create Date:        2022-04-12
Author:             Mike Fickley
Description:        Pulls enabled measures out of QDW in a format that can be put back through the 
                    the measure_config_ui app
SQL Syntax:         TSQL
Environment:        Any WAREHOUSE DB in QDW
****************************************************************************************************/

select
    i.name as initiative
, coalesce(qst.CalendarYear,datepart(year,getdate())) as year
, im.MeasureDescription as description
, im.MeasureDisplayName as frontendName
, im.MeasureShortName as shortName
, am.MeasureID
, am.name as backendName
, am.rate as rate
, '' as script
, coalesce(cast(qst.Threshold1 as decimal(10,4)),0) as threshold1
, coalesce(cast(qst.Threshold2 as decimal(10,4)),0) as threshold2
, coalesce(cast(qst.Threshold3 as decimal(10,4)),0) as threshold3
, coalesce(cast(qst.Threshold4 as decimal(10,4)),im.threshold) as threshold4
, im.ThresholdDirection as thresholdDirection
from web.InitiativeMeasure im
    inner join web.Initiative i on im.InitiativeID = i.InitiativeID
    inner join rpt.ArcasMeasure am on im.measureid = am.measureid
    left join web.QualityScoreThreshold qst
    on im.MeasureID = qst.MeasureID
        and im.InitiativeID = qst.InitiativeID
		and qst.CalendarYear = (select max(calendaryear) from web.QualityScoreThreshold)
where im.MeasureEnabled = 1
    and i.InitiativeEnabled = 1
order by 1,2,3,4,5,6,7,8