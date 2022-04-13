/***************************************************************************************************
Create Date:        2022-04-12
Author:             Mike Fickley
Description:        Pulls enabled measures out of QDW in a format that can be put back through the 
                    the measure_config_ui app
SQL Syntax:         TSQL
Environment:        Any WAREHOUSE DB in QDW
****************************************************************************************************/

declare @staging_db as varchar(50) = (select name from sys.databases where name like '%[_]staging[_]%')
declare @tsql as nvarchar(max);

-- building temp table for qualityscoreweight --
IF OBJECT_ID('tempdb.dbo.#qsw', 'U') IS NOT NULL
  DROP TABLE #qsw;

select InitiativeID
, MeasureID
, CalendarYear [calendarYear]
, location_display_name [locationDisplayName] 
, Weight
, Baseline
into #qsw
from web.qualityscoreweight q	
left join Location_Master lm on q.LocationID = lm.path_segment

-- building temp table for payersuppliedmeasures --
IF OBJECT_ID('tempdb.dbo.#psm', 'U') IS NOT NULL
  DROP TABLE #psm;

CREATE TABLE #psm 
(
	payerSource varchar(255)
	, payerMeasureName varchar(255)
	, arcadiaMeasureName varchar(50)
	, arcadiaMeasureRate varchar(50)
)

set @tsql = '
insert into #psm
select m.source_id [payerSource]
, m.source [payerMeasureName]
, m.destination [arcadiaMeasureName]
, m.destination_rate [arcadiaMeasureRate]
from '+@staging_db+'.lookup.measure m
'
print @tsql
exec sp_executesql @tsql

-- main output --
select
ROW_NUMBER() OVER(order by i.name,am.name,am.rate) AS rowNum
,  i.name [initiativeName]
, am.name [backendName]
, am.rate [rate]
, im.Threshold
, im.ThresholdDirection
, im.MeasureDisplayName [displayName]
, im.MeasureDescription [displayDescription]
, im.MeasureShortName [displayShortName]
--, am.MeasureID
--, '' as script
, qst.CalendarYear [qst_calendarYear]
, qst.Threshold1 [qst_Threshold1]
, qst.Threshold2 [qst_Threshold2]
, qst.Threshold3 [qst_Threshold3]
, qst.Threshold4 [qst_Threshold4]
, qst.Factor0 [qst_Factor0]
, qst.Factor1 [qst_Factor1]
, qst.Factor2 [qst_Factor2]
, qst.Factor3 [qst_Factor3]
, qst.Factor4 [qst_Factor4]
, #qsw.CalendarYear [qsw_calendarYear]
, #qsw.locationDisplayName [qsw_locationDisplayName]
, #qsw.Weight [qsw_weight]
, #qsw.Baseline [qsw_baseline]
, #psm.payerSource
, #psm.payerMeasureName
, #psm.arcadiaMeasureName
, #psm.arcadiaMeasureRate
, li.LobName
from web.InitiativeMeasure im
    inner join web.Initiative i on im.InitiativeID = i.InitiativeID
    inner join rpt.ArcasMeasure am on im.measureid = am.measureid
    left join web.QualityScoreThreshold qst
		on im.MeasureID = qst.MeasureID
        and im.InitiativeID = qst.InitiativeID
		and qst.CalendarYear = (select max(calendaryear) from web.QualityScoreThreshold)
	left join #qsw
		on im.MeasureID = #qsw.MeasureID
		and im.InitiativeID = #qsw.InitiativeID
	left join #psm
		on #psm.arcadiaMeasureName = am.name
		and #psm.arcadiaMeasureRate = am.rate
	left join web.LobInitiative li
		on li.InitiativeId = im.InitiativeID
where im.MeasureEnabled = 1
    and i.InitiativeEnabled = 1
order by 1,2,3,4,5,6,7,8