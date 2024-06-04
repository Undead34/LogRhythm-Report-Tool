from datetime import date, datetime, time
import pandas as pd
import pyodbc
import sys

from utils.constants import DB_HOST, DB_USER, DB_PASS


class MSQLServer:
    def __init__(self) -> None:
        driver = f"DRIVER={{SQL Server}};SERVER={DB_HOST};UID={DB_USER};PWD={DB_PASS}"
        self._conn = pyodbc.connect(driver)
        self.entity_ids: pd.DataFrame | None = None

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
        columns = ['EntityID', 'ParentEntityID', 'Name',
                   'FullName', 'ShortDesc', 'RecordStatus', 'DateUpdated']
        return pd.DataFrame([tuple(row) for row in data], columns=columns)

    def _validate_entity_ids(self):
        if self.entity_ids is None or self.entity_ids.empty:
            print("Error: Se llamó a la base de datos sin setear los Entity IDs")
            sys.exit(1)

    def count_alarms(self):
        self._validate_entity_ids()

        # Extraer los EntityID del DataFrame
        entity_ids = self.entity_ids['EntityID'].tolist()
        entity_ids_str = ', '.join(map(str, entity_ids))

        sql = f"""
        SELECT
            count(*) as Count
        FROM
            LogRhythm_Alarms.dbo.Alarm a with (NOLOCK)
            JOIN
            LogRhythmEMDB.dbo.AlarmRule ar
            ON a.AlarmRuleID = ar.AlarmRuleID
        WHERE
            Entity.EntityID IN ({entity_ids_str}) AND
            ar.AlarmType = 5 AND
            DateInserted BETWEEN '2024-04-01T04:00:00Z' AND '2024-05-01T03:59:59Z'
        """
        cursor = self._conn.execute(sql)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def alarms_per_entity(self):
        self._validate_entity_ids()

        # Extraer los EntityID del DataFrame
        entity_ids = self.entity_ids['EntityID'].tolist()
        entity_ids_str = ', '.join(map(str, entity_ids))

        sql = f"""
        SELECT 
            Entity.Name AS 'Entity',
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
            END)) AS Alarm_Status,
            COUNT(AlarmName.Name) AS Alarm_Count
        FROM 
            [LogRhythm_Alarms].[dbo].[Alarm] AS Alarm 
            JOIN LogRhythmEMDB.dbo.AlarmRule AS AlarmName 
                ON Alarm.AlarmRuleID = AlarmName.AlarmRuleID
            JOIN LogRhythmEMDB.dbo.Entity AS Entity 
                ON Entity.EntityID = Alarm.EntityID
        WHERE 
            Entity.EntityID IN ({entity_ids_str}) AND
            DateInserted BETWEEN '2024-04-01T16:00:00Z' AND '2024-05-01T03:59:59Z'
        GROUP BY 
            Entity.Name, AlarmStatus
        ORDER BY
            [AlarmStatus] DESC
        """
        cursor = self._conn.execute(sql)
        data = cursor.fetchall()
        for row in data:
            print(row)

    def alarms_per_entity_table(self) -> pd.DataFrame:
        self._validate_entity_ids()

        # Extraer los EntityID del DataFrame
        entity_ids = self.entity_ids['EntityID'].tolist()
        entity_ids_str = ', '.join(map(str, entity_ids))

        sql = f"""
        SELECT 
            Entity.Name AS 'Entity',
            Alarm.AlarmDate,
            Alarm.AlarmID,
            AlarmName.Name,
            (CONVERT(nvarchar, CASE
                WHEN AlarmStatus = 4 THEN 'Auto Closed'
                WHEN AlarmStatus = 8 THEN 'Reported'
                WHEN AlarmStatus = 6 THEN 'Resolved'
                WHEN AlarmStatus = 5 THEN 'False Positive'
                WHEN AlarmStatus = 0 THEN 'New'
                WHEN AlarmStatus = 1 THEN 'OpenAlarm'
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
            DateInserted BETWEEN '2024-04-01T16:00:00Z' AND '2024-05-01T03:59:59Z'
        ORDER BY
            [AlarmStatus] DESC
        """
        cursor = self._conn.execute(sql)
        # Convertir los datos a un DataFrame de pandas
        data = cursor.fetchall()
        columns = ['Entity', 'AlarmDate',
                   'AlarmID', 'AlarmName', 'AlarmStatus']
        df = pd.DataFrame([tuple(row) for row in data], columns=columns)

        return df

    def set_entity_ids(self, entity_ids: pd.DataFrame):
        if not isinstance(entity_ids, pd.DataFrame):
            raise ValueError("entity_ids debe ser un DataFrame de pandas")
        self.entity_ids = entity_ids

    def get_alarm_details(self) -> pd.DataFrame:
        self._validate_entity_ids()

        # Extraer los EntityID del DataFrame
        entity_ids = self.entity_ids['EntityID'].tolist()
        entity_ids_str = ', '.join(map(str, entity_ids))

        # Consulta 1: Extraer datos de Alarm y AlarmRule
        sql = f"""
        -- Parte 1: Obtener los IDs de Alarmas relevantes
        WITH AlarmIDs AS (
            SELECT alm.[AlarmID]
            FROM [LogRhythm_Alarms].[dbo].[Alarm] alm WITH (NOLOCK)
            WHERE alm.[EntityID] IN ({entity_ids_str})
            AND alm.[DateInserted] BETWEEN '2024-04-01T16:00:00Z' AND '2024-05-01T03:59:59Z'
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
            'EntityID', 'AlarmID', 'AlarmRuleID', 'AlarmStatus', 'AlarmStatusText',
            'AlarmDate', 'DateInserted', 'DateUpdated', 'MARCMsgID', 'AlarmType',
            'Name', 'Enabled', 'MsgID', 'Priority'
        ]

        df = pd.DataFrame([tuple(row) for row in data], columns=columns)

        return df

    def set_date_range(self, dates: tuple[date, date]):
        start, end = dates
        # Asegúrate de que el tiempo final sea 23:59:59 para incluir todo el día final
        end = datetime.combine(end, time(23, 59, 59))

        start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"Formatted start date: {start_str}")
        print(f"Formatted end date: {end_str}")