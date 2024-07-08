from datetime import datetime
import pandas as pd
import pyodbc
import sys

from src.utils.constants import DB_HOST, DB_USER, DB_PASS

class MSQLServer:
    def __init__(self) -> None:
        driver = f"DRIVER={{SQL Server}};SERVER={DB_HOST};UID={DB_USER};PWD={DB_PASS}"
        self._conn = pyodbc.connect(driver)
        self._entity_ids: pd.DataFrame | None = None

        self._start_date: str | None = None
        self._end_date: str | None = None

        self._cache = {}

    @staticmethod
    def get_entities() -> pd.DataFrame:
        sql = """
        SELECT TOP (1000) [EntityID], [ParentEntityID], [Name],
               [FullName], [ShortDesc], [RecordStatus], [DateUpdated]
        FROM [LogRhythmEMDB].[dbo].[Entity]
        """
        driver = f"DRIVER={{SQL Server}};SERVER={DB_HOST};UID={DB_USER};PWD={DB_PASS}"
        _conn = pyodbc.connect(driver)
        cursor = _conn.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame([tuple(row) for row in data], columns=columns)

        _conn.close()
        
        return df

    def get_alarm_count(self) -> int:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT count(*) as Count
        FROM LogRhythm_Alarms.[dbo].[Alarm] a WITH (NOLOCK)
        WHERE a.[EntityID] IN ({entity_ids_str}) 
          AND DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
        """
        result = self._execute_query(sql)
        return result.iloc[0]['Count']

    def get_alarm_summary_by_entity_and_status(self) -> pd.DataFrame:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT Entity.Name AS 'EntityName',
               Alarm.AlarmStatus,
               COUNT(*) AS AlarmCount
        FROM [LogRhythm_Alarms].[dbo].[Alarm] AS Alarm 
        JOIN LogRhythmEMDB.dbo.Entity AS Entity 
          ON Entity.EntityID = Alarm.EntityID
        WHERE Entity.EntityID IN ({entity_ids_str}) 
          AND DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
        GROUP BY Entity.Name, Alarm.AlarmStatus
        ORDER BY Alarm.AlarmStatus DESC
        """
        df = self._execute_query(sql).copy()

        df['AlarmStatus'] = df['AlarmStatus'].fillna(-1).astype(int).map({
            -1: 'Unknown', 0: 'New', 1: 'OpenAlarm', 2: 'Working', 3: 'Escalated', 4: 'AutoClosed', 
            5: 'FalsePositive', 6: 'Resolved', 7: 'UnResolved', 8: 'Reported', 9: 'Monitor'
        })

        return df

    def get_alarms_information(self) -> pd.DataFrame:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT *,
            DATEDIFF(SECOND, GeneratedOn, InvestigatedOn) AS TTD,
            DATEDIFF(SECOND, InvestigatedOn, ClosedOn) AS TTR
        FROM LogRhythm_Alarms.dbo.vw_LatestAlarms
        WHERE EntityID IN ({entity_ids_str})
          AND DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
        """
        df = self._execute_query(sql).copy()
        
        df['AlarmStatus'] = df['AlarmStatus'].fillna(-1).astype(int).map({
            -1: 'Unknown', 0: 'New', 1: 'OpenAlarm', 2: 'Working', 3: 'Escalated', 4: 'AutoClosed', 
            5: 'FalsePositive', 6: 'Resolved', 7: 'UnResolved', 8: 'Reported', 9: 'Monitor'
        })

        return df

    def get_full_alarm_details(self) -> pd.DataFrame:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT alm.[EntityID],
               alm.[AlarmDate],
               alm.[DateInserted],
               alm.[DateUpdated],
               alm.[AlarmStatus],
               emsg.[AlarmType],
               emsg.[Name] AS AlarmName,
               lrem.[Priority]
        FROM [LogRhythm_Alarms].[dbo].[Alarm] alm WITH (NOLOCK)
        JOIN LogRhythmEMDB.dbo.AlarmRule emsg WITH (NOLOCK)
          ON alm.[AlarmRuleID] = emsg.[AlarmRuleID]
        JOIN [LogRhythm_Alarms].[dbo].[AlarmToMARCMsg] atm WITH (NOLOCK)
          ON alm.[AlarmID] = atm.[AlarmID]
        JOIN [LogRhythm_Events].[dbo].[Msg] lrem WITH (NOLOCK)
          ON lrem.[MsgID] = atm.[MARCMsgID]
        WHERE alm.[EntityID] IN ({entity_ids_str})
          AND alm.[DateInserted] BETWEEN '{self._start_date}' AND '{self._end_date}'
        """
        df = self._execute_query(sql).copy()
        
        df['AlarmStatus'] = df['AlarmStatus'].fillna(-1).astype(int).map({
            -1: 'Unknown', 0: 'New', 1: 'OpenAlarm', 2: 'Working', 3: 'Escalated', 4: 'AutoClosed', 
            5: 'FalsePositive', 6: 'Resolved', 7: 'UnResolved', 8: 'Reported', 9: 'Monitor'
        })

        return df

    def get_alarm_durations(self) -> pd.DataFrame:
        self._validate_entity_ids()
        self._validate_dates()

        entity_ids_str = self._get_entities_id()

        sql = f"""
        SELECT 
            EntityID,
            AlarmDate,
            DateInserted,
            GeneratedOn,
            InvestigatedOn,
            ClosedOn,
            AlarmRuleName AS AlarmName,
            MsgClassName,
            AlarmPriority,
            AlarmStatus,
            DATEDIFF(SECOND, GeneratedOn, InvestigatedOn) AS TTD,
            DATEDIFF(SECOND, InvestigatedOn, ClosedOn) AS TTR
        FROM LogRhythm_Alarms.dbo.vw_LatestAlarms
        WHERE EntityID IN ({entity_ids_str})
          AND DateInserted BETWEEN '{self._start_date}' AND '{self._end_date}'
          AND GeneratedOn IS NOT NULL
          AND InvestigatedOn IS NOT NULL
        """
        df = self._execute_query(sql).copy()
        
        df['AlarmStatus'] = df['AlarmStatus'].fillna(-1).astype(int).map({
            -1: 'Unknown', 0: 'New', 1: 'OpenAlarm', 2: 'Working', 3: 'Escalated', 4: 'AutoClosed', 
            5: 'FalsePositive', 6: 'Resolved', 7: 'UnResolved', 8: 'Reported', 9: 'Monitor'
        })
        
        # Filtrar registros con TTD y TTR negativos
        df = df[(df['TTD'] >= 0) & (df['TTR'] >= 0)]
        
        return df
    
    def get_TTD_AND_TTR_by_alarm_priority(self) -> pd.DataFrame:
        df = self.get_alarm_durations()
        summary = df.groupby('AlarmPriority').agg(
            Tickets=('EntityID', 'count'),
            Avg_TTD=('TTD', 'mean'),
            Max_TTD=('TTD', 'max'),
            Avg_TTR=('TTR', 'mean'),
            Max_TTR=('TTR', 'max')
        ).reset_index()
        summary.columns = ['Priority', 'Count', 'Avg_TTD', 'Max_TTD', 'Avg_TTR', 'Max_TTR']
        return summary
    
    def get_TTD_AND_TTR_by_msg_class_name(self) -> pd.DataFrame:
        df = self.get_alarm_durations()
        summary = df.groupby('MsgClassName').agg(
            Tickets=('EntityID', 'count'),
            Avg_TTD=('TTD', 'mean'),
            Max_TTD=('TTD', 'max'),
            Avg_TTR=('TTR', 'mean'),
            Max_TTR=('TTR', 'max')
        ).reset_index()

        summary.columns = ['MsgClassName', 'Count', 'Avg_TTD', 'Max_TTD', 'Avg_TTR', 'Max_TTR']
        return summary
    
    # ==========================================
    # Private methods
    # ==========================================

    def _execute_query(self, sql: str) -> pd.DataFrame:
        cache_key = (sql, self._get_entities_id(), self._start_date, self._end_date)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        cursor = self._conn.execute(sql)
        data = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame([tuple(row) for row in data], columns=columns)
        self._cache[cache_key] = df
        
        return df

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
        self._cache.clear()

    def set_date_range(self, start_date: datetime, end_date: datetime) -> None:
        self._start_date = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        self._end_date = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        self._cache.clear()

    def _get_entities_id(self) -> str:
        if self._entity_ids is None:
            return ""
        entity_ids = self._entity_ids['EntityID'].tolist()
        return ', '.join(map(str, entity_ids))
