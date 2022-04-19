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
,  i.name [initiative]
, am.name [measure]
, am.rate [rate]
, cast(im.Threshold as decimal(10,4)) [threshold]
, im.ThresholdDirection [thresholddirection]
, im.MeasureDisplayName [displayname]
, im.MeasureDescription [displaydescription]
, im.MeasureShortName [displayshortname]
--, am.MeasureID
--, '' as script
, qst.CalendarYear [qst_calendaryear]
, qst.Threshold1 [threshold1]
, qst.Threshold2 [threshold2]
, qst.Threshold3 [threshold3]
, qst.Threshold4 [threshold4]
, qst.Factor0 [factor0]
, qst.Factor1 [factor1]
, qst.Factor2 [factor2]
, qst.Factor3 [factor3]
, qst.Factor4 [factor4]
, #qsw.CalendarYear [qsw_calendaryear]
, #qsw.locationDisplayName [locationdisplayname]
, #qsw.Weight [weight]
, #qsw.Baseline [baseline]
, #psm.payerSource [sourcepartition]
, #psm.payerMeasureName [payersuppliedname]
, #psm.arcadiaMeasureName [arcadianame]
, #psm.arcadiaMeasureRate [arcadiarate]
, li.lobName [lobname]
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