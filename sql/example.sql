SELECT TOP (100) *
FROM (
    SELECT 
        alm.[EntityID],
        alm.[AlarmID],
        alm.[AlarmRuleID],
        alm.[AlarmStatus],
        CASE 
            WHEN alm.[AlarmStatus] = 0 THEN 'New'
            WHEN alm.[AlarmStatus] = 1 THEN 'OpenAlarm'
            WHEN alm.[AlarmStatus] = 2 THEN 'Working'
            WHEN alm.[AlarmStatus] = 3 THEN 'Escalated'
            WHEN alm.[AlarmStatus] = 4 THEN 'AutoClosed'
            WHEN alm.[AlarmStatus] = 5 THEN 'FalsePositive'
            WHEN alm.[AlarmStatus] = 6 THEN 'Resolved'
            WHEN alm.[AlarmStatus] = 7 THEN 'UnResolved'
            WHEN alm.[AlarmStatus] = 8 THEN 'Reported'
            WHEN alm.[AlarmStatus] = 9 THEN 'Monitor'
            ELSE 'Unknown'
        END AS Alarm_Status_Text,
        alm.[AlarmDate],
        alm.[DateInserted],
        alm.[DateUpdated],
        atm.[MARCMsgID],
        emsg.[AlarmType],
        emsg.[Name],
        emsg.[Enabled]
    FROM [LogRhythm_Alarms].[dbo].[Alarm] alm WITH (NOLOCK)
    JOIN [LogRhythm_Alarms].[dbo].[AlarmToMARCMsg] atm WITH (NOLOCK)
        ON alm.[AlarmID] = atm.[AlarmID]
    JOIN LogRhythmEMDB.dbo.AlarmRule emsg WITH (NOLOCK)
        ON alm.[AlarmRuleID] = emsg.[AlarmRuleID]
) almm
JOIN (
    SELECT 
        MsgID,
        Priority
    FROM LogRhythm_Events.dbo.Msg WITH (NOLOCK)
) emsg 
    ON emsg.MsgID = almm.MARCMsgID
ORDER BY almm.DateInserted DESC;
