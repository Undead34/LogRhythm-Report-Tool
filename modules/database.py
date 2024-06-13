from datetime import date, datetime, time
import pandas as pd
import pyodbc
import sys

from utils.constants import DB_HOST, DB_USER, DB_PASS


class MSQLServer:
    def __init__(self) -> None:
        driver = f"DRIVER={{SQL Server}};SERVER={DB_HOST};UID={DB_USER};PWD={DB_PASS}"
        self._conn = pyodbc.connect(driver)
        self._entity_ids: pd.DataFrame | None = None

        self._start_date: str | None = None
        self._end_date: str | None = None

        self._alarm_details_cache = None
        self._alarm_durations_cached = None

    def get_full_alarm_details_cached(self):
        if self._alarm_details_cache is None:
            self._alarm_details_cache = self.get_full_alarm_details()
        return self._alarm_details_cache
    
    def get_alarm_durations_cached(self):
        if self._alarm_durations_cached is None:
            self._alarm_durations_cached = self.get_alarm_durations()
        return self._alarm_durations_cached

    def _validate_entity_ids(self):
        if self._entity_ids is None or self._entity_ids.empty:
            print("Error: Se llamó a la base de datos sin setear los Entity IDs")
            sys.exit(1)

    def _validate_dates(self):
        if self._start_date is None or self._end_date is None:
            print("Error: Se llamó a la base de datos sin setear las fechas")
            sys.exit(1)

    def set_entity_ids(self, entity_ids: pd.DataFrame):
        if not isinstance(entity_ids, pd.DataFrame):
            raise ValueError("entity_ids debe ser un DataFrame de pandas")
        self._entity_ids = entity_ids

    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        self._start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        self._end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _get_entities_id(self) -> str:
        # Extraer los EntityID del DataFrame
        entity_ids = self._entity_ids['EntityID'].tolist()
        entity_ids_str = ', '.join(map(str, entity_ids))
        return entity_ids_str

    def get_entities(self) -> pd.DataFrame:
        sql = """   
        SELECT TOP (1000) [EntityID]
            ,[ParentEntityID]
            ,[Name] 
            ,[FullName]
            ,[ShortDesc]
            ,[RecordStatus]
            ,[DateUpdated]
        FROM [LogRhythmEMDB].[dbo].[Entity]
        """

        cursor = self._conn.execute(sql)
        data = cursor.fetchall()
        columns = ['EntityID', 'ParentEntityID',
                   'Name', 'FullName',
                   'ShortDesc', 'RecordStatus',
                   'DateUpdated']

        return pd.DataFrame([tuple(row) for row in data], columns=columns)

    def get_alarm_count(self) -> int:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT
            count(*) as Count
        FROM
            LogRhythm_Alarms.[dbo].[Alarm] a with (NOLOCK)
            JOIN
            LogRhythmEMDB.[dbo].[AlarmRule] ar
            ON a.[AlarmRuleID] = ar.[AlarmRuleID]
        WHERE
            ar.[AlarmType] = 5 AND
            a.[EntityID] IN ({entity_ids_str}) AND
            DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
        """

        cursor = self._conn.execute(sql)
        data = cursor.fetchall()
        return data[0][0]

    def get_alarm_summary_by_entity_and_status(self) -> pd.DataFrame:
        """
        Esta consulta obtiene el nombre de la entidad, el estado de la alarma y el conteo de alarmas agrupado por entidad y estado de alarma.
        """
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT 
            Entity.Name AS 'EntityName',
            (CONVERT(nvarchar, CASE
                WHEN AlarmStatus = 0 THEN 'New'
                WHEN AlarmStatus = 1 THEN 'OpenAlarm'
                WHEN AlarmStatus = 2 THEN 'Working'
                WHEN AlarmStatus = 3 THEN 'Escalated'
                WHEN AlarmStatus = 4 THEN 'AutoClosed'
                WHEN AlarmStatus = 5 THEN 'FalsePositive'
                WHEN AlarmStatus = 6 THEN 'Resolved'
                WHEN AlarmStatus = 7 THEN 'UnResolved'
                WHEN AlarmStatus = 8 THEN 'Reported'
                WHEN AlarmStatus = 9 THEN 'Monitor' 
            END)) AS AlarmStatus,
            COUNT(AlarmName.Name) AS AlarmCount
        FROM 
            [LogRhythm_Alarms].[dbo].[Alarm] AS Alarm 
            JOIN LogRhythmEMDB.dbo.AlarmRule AS AlarmName 
                ON Alarm.AlarmRuleID = AlarmName.AlarmRuleID
            JOIN LogRhythmEMDB.dbo.Entity AS Entity 
                ON Entity.EntityID = Alarm.EntityID
        WHERE 
            Entity.EntityID IN ({entity_ids_str}) AND
            DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
        GROUP BY 
            Entity.Name, AlarmStatus
        ORDER BY
            [AlarmStatus] DESC
        """

        cursor = self._conn.execute(sql)
        data = cursor.fetchall()
        columns = ['EntityName', 'AlarmStatus', 'AlarmCount']

        return pd.DataFrame([tuple(row) for row in data], columns=columns)

    def get_alarm_details_by_entity(self) -> pd.DataFrame:
        """
        Obtiene detalles de alarmas específicas (como la fecha de la alarma, el ID de la alarma, el nombre y el estado de la alarma) agrupados por entidad
        """
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT 
            Entity.Name AS 'EntityName',
            Alarm.AlarmDate,
            Alarm.AlarmID,
            AlarmName.Name,
            (CONVERT(nvarchar, CASE
                WHEN AlarmStatus = 4 THEN 'Auto Closed'
                WHEN AlarmStatus = 8 THEN 'Reported'
                WHEN AlarmStatus = 6 THEN 'Resolved'
                WHEN AlarmStatus = 5 THEN 'False Positive'
                WHEN AlarmStatus = 0 THEN 'New'
                WHEN AlarmStatus = 1 THEN 'Open Alarm'
                WHEN AlarmStatus = 9 THEN 'Monitor' 
            END)) AS AlarmStatus
        FROM 
            [LogRhythm_Alarms].[dbo].[Alarm] AS Alarm 
            JOIN LogRhythmEMDB.dbo.AlarmRule AS AlarmName 
                ON Alarm.AlarmRuleID = AlarmName.AlarmRuleID
            JOIN LogRhythmEMDB.dbo.Entity AS Entity 
                ON Entity.EntityID = Alarm.EntityID
        WHERE 
            Entity.EntityID IN ({entity_ids_str}) AND
            DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
        ORDER BY
            [AlarmStatus] DESC
        """

        cursor = self._conn.execute(sql)
        data = cursor.fetchall()

        columns = ['Entity Name', 'Alarm Date',
                   'Alarm ID', 'Alarm Name', 'Alarm Status']

        return pd.DataFrame([tuple(row) for row in data], columns=columns)

    def get_full_alarm_details(self) -> pd.DataFrame:
        """
        Esta consulta, se divide en dos partes: primero obtiene los IDs de las alarmas relevantes y luego obtiene los datos completos usando esos IDs
        """
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        # Consulta 1: Extraer datos de Alarm y AlarmRule
        sql = f"""
        -- Parte 1: Obtener los IDs de Alarmas relevantes
        WITH AlarmIDs AS (
            SELECT alm.[AlarmID]
            FROM [LogRhythm_Alarms].[dbo].[Alarm] alm WITH (NOLOCK)
            WHERE alm.[EntityID] IN ({entity_ids_str})
            AND alm.[DateInserted] BETWEEN '{self._start_date}' AND '{self._end_date}'
        )
        -- Parte 2: Obtener los datos completos usando los IDs de Alarmas
        SELECT
            alm.[EntityID],
            alm.[AlarmDate],
            alm.[DateInserted],
            alm.[DateUpdated],
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
            END AS AlarmStatus,
            emsg.[AlarmType],
            emsg.[Name],
            lrem.[Priority]
        FROM AlarmIDs ids
        JOIN [LogRhythm_Alarms].[dbo].[Alarm] alm WITH (NOLOCK)
            ON ids.[AlarmID] = alm.[AlarmID]
        JOIN LogRhythmEMDB.dbo.AlarmRule emsg WITH (NOLOCK)
            ON alm.[AlarmRuleID] = emsg.[AlarmRuleID]
        JOIN [LogRhythm_Alarms].[dbo].[AlarmToMARCMsg] atm WITH (NOLOCK)
            ON alm.[AlarmID] = atm.[AlarmID]
        JOIN [LogRhythm_Events].[dbo].[Msg] lrem WITH (NOLOCK)
            ON lrem.[MsgID] = atm.[MARCMsgID];
        """
        cursor = self._conn.execute(sql)
        data = cursor.fetchall()

        # Especificar los nombres de las columnas
        columns = [
            'EntityID', 'AlarmDate',
            'DateInserted', 'DateUpdated',
            'AlarmStatus', 'AlarmType',
            'AlarmName', 'AlarmPriority',
        ]

        return pd.DataFrame([tuple(row) for row in data], columns=columns)

    def get_alarm_durations(self) -> pd.DataFrame:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        WITH AlarmIDs AS (
            SELECT alm.[AlarmID]
            FROM [LogRhythm_Alarms].[dbo].[Alarm] alm WITH (NOLOCK)
            WHERE alm.[EntityID] IN ({entity_ids_str})
            AND alm.[DateInserted] BETWEEN '{self._start_date}' AND '{self._end_date}'
        )
        SELECT 
            a.EntityID,
            a.AlarmDate,
            a.DateInserted,
            am.GeneratedOn,
            am.OpenedOn,
            am.InvestigatedOn,
            am.ClosedOn,
            ar.[Name] AS AlarmName,
            lrem.[Priority],
            DATEDIFF(SECOND, am.GeneratedOn, am.InvestigatedOn) AS TTD,
            DATEDIFF(SECOND, am.InvestigatedOn, am.ClosedOn) AS TTR,
            CASE 
                WHEN a.AlarmStatus = 0 THEN 'New'
                WHEN a.AlarmStatus = 1 THEN 'OpenAlarm'
                WHEN a.AlarmStatus = 2 THEN 'Working'
                WHEN a.AlarmStatus = 3 THEN 'Escalated'
                WHEN a.AlarmStatus = 4 THEN 'AutoClosed'
                WHEN a.AlarmStatus = 5 THEN 'FalsePositive'
                WHEN a.AlarmStatus = 6 THEN 'Resolved'
                WHEN a.AlarmStatus = 7 THEN 'UnResolved'
                WHEN a.AlarmStatus = 8 THEN 'Reported'
                WHEN a.AlarmStatus = 9 THEN 'Monitor'
                ELSE 'Unknown'
            END AS AlarmStatus,
            ar.[AlarmType]
        FROM AlarmIDs ids
        JOIN LogRhythm_Alarms.dbo.Alarm a WITH (NOLOCK)
            ON ids.[AlarmID] = a.[AlarmID]
        JOIN LogRhythm_Alarms.dbo.AlarmToMARCMsg atm WITH (NOLOCK) 
            ON a.AlarmID = atm.AlarmID
        JOIN [LogRhythm_Alarms].[dbo].[AlarmMetrics] am WITH (NOLOCK) 
            ON a.AlarmID = am.AlarmID
        JOIN [LogRhythmEMDB].[dbo].AlarmRule ar
            ON a.AlarmRuleID = ar.AlarmRuleID 
        JOIN [LogRhythm_Events].[dbo].[Msg] lrem WITH (NOLOCK)
            ON lrem.[MsgID] = atm.[MARCMsgID]
        WHERE 
            a.[EntityID] IN ({entity_ids_str})
            AND a.DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
            AND am.GeneratedOn IS NOT NULL
            AND am.InvestigatedOn IS NOT NULL
        """
        cursor = self._conn.execute(sql)
        data = cursor.fetchall()

        columns = [
            'EntityID', 'AlarmDate', 'DateInserted', 'GeneratedOn', 'OpenedOn', 
            'InvestigatedOn', 'ClosedOn', 'AlarmName', 'Priority', 'TTD', 'TTR', 
            'AlarmStatus', 'AlarmType'
        ]

        return pd.DataFrame([tuple(row) for row in data], columns=columns)
