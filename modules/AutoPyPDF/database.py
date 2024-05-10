from elasticsearch import Elasticsearch
from .querys import Querys
from .utils import dates
import pyodbc
import time
import os


class Database():
    def __init__(self):
        host = os.environ["HOST"]
        username = os.environ["DBUSER"]
        password = os.environ["DBPASS"]

        self.ranges = dates.get_current_month_range()

        driver = "DRIVER=%s;SERVER=%s;UID=%s;PWD=%s" % (
            "{SQL Server}", host, username, password)
        self.conn = pyodbc.connect(driver)
        self.esearch = Elasticsearch(["http://localhost:9200"])

    def ESearch(self, query):
        _range = query["query"]["bool"]["must"][3]["range"]["normalDate"]
        _range["gte"] = self.ranges["gte"]
        _range["lte"] = self.ranges["lte"]

        return self.esearch.search(index="logs-*", body=query)

    def getAttackers(self):
        results = self.ESearch(Querys["Attackers"])
        print(results)
    
    def getTop10Vulns(self):
        results = self.ESearch(Querys["Top10Vulns"])
        print(results)

    def getAuditViolations(self):
        results = self.ESearch(Querys["AuditViolations"])
        print(results)



# def getNetworkAllowed(self):
#     query = Querys["network"]["allowed"]
#     range = query["query"]["bool"]["must"][3]["range"]["normalDate"]

#     range["lte"] = dates.toMilliseconds(self.ranges["to"])
#     range["gte"] = dates.toMilliseconds(self.ranges["from"])

#     results = self.esearch.search(index="logs-*", body=query)
#     print(results)

# def getNetworkDenied(self):
#     query = Querys["network"]["denied"]
#     # self.esearch.search(index="logs-*", body=query)

# def getNetworkAllowVsDeny(self):
#     query = Querys["network"]["allow_vs_deny"]
#     # self.esearch.search(index="logs-*", body=query)

# def getGeneralAVGRiskByTop10Events(self):
#     pass

# def getEntityTopSecurityEvents(self):
#     pass


# for row in rows:
#     print('user %s logged on at %s' % (row.user_id, row.last_logon))
# sqlQuery = """SELECT * FROM table WHERE date >= DATEADD(day, -30, GETDATE())"""
# conn.execute("SELECT TOP 10 * FROM StatsSystemMonitorCountsMinute;")

    # def getEventsVsLogs(self):
    #     query = Querys["EventsVsLogs"]
    #     range = query["query"]["bool"]["must"][3]["range"]["normalDate"]
    #     ago, now = self._getMillisTime(2_592_000)

    #     range["gte"] = ago
    #     range["lte"] = now

    #     results = self.esearch.search(index="logs-*", body=query)["aggregations"]["2"]["buckets"]
    #     return results["Events"]["doc_count"], results["Logs"]["doc_count"]

    # def _getMillisTime(self, seconds: int = 0):
    #     now = int(time.time() * 1000)
    #     secondsAgo = now - (seconds * 1000)

    #     return secondsAgo, now

    # def getEPSTable(self):
    #     query = Querys["EPSTable"]
    #     range = query["query"]["bool"]["must"][3]["range"]["normalDate"]
    #     ago, now = self._getMillisTime(900)

    #     range["gte"] = ago
    #     range["lte"] = now

    #     results = self.esearch.search(index="logs-*", body=query)
    #     return results["aggregations"]["2"]["buckets"][0]

    # def getAlarms(self):
    #     sql = f"""
    #         select Entity.Name as 'Entity',
    #         (Convert(nvarchar, Case
    #         When AlarmStatus = 0 Then 'New'
    #         When AlarmStatus = 1 Then 'OpenAlarm'
    #         When AlarmStatus = 2 Then 'Working'
    #         When AlarmStatus = 3 Then 'Escalated'
    #         When AlarmStatus = 4 Then 'AutoClosed'
    #         When AlarmStatus = 5 Then 'FalsePositive'
    #         When AlarmStatus = 6 Then 'Resolved'
    #         When AlarmStatus = 7 Then 'UnResolved'
    #         When AlarmStatus = 8 Then 'Reported'
    #         When AlarmStatus = 9 Then 'Monitor' End)) as Alarm_Status,
    #         Count(AlarmName.Name) as Alarm_Count
    #         from [LogRhythm_Alarms].[dbo].[Alarm] as Alarm join LogRhythmEMDB.dbo.AlarmRule as AlarmName on Alarm.AlarmRuleID=AlarmName.AlarmRuleID
    #         join LogRhythmEMDB.dbo.Entity as Entity on Entity.EntityID=Alarm.EntityID
    #         WHERE DateInserted BETWEEN '{dates.getISODate(30)}' AND '{dates.getISODate()}' AND Entity.EntityID = 16
    #         Group by Entity.Name, AlarmStatus
    #         ORDER BY
    #         [Alarm_Count] DESC
    #         """
    #     cursor = self.conn.cursor()
    #     cursor.execute(sql)
    #     rows = cursor.fetchall()
    #     cursor.close()
    #     return rows

    # def getTotalAlarms(self):
    #     sql = f"""
    #         SELECT
    #             count(*) as Count
    #         FROM
    #             LogRhythm_Alarms.dbo.Alarm a with (NOLOCK)
    #             JOIN
    #             LogRhythmEMDB.dbo.AlarmRule ar
    #                 ON a.AlarmRuleID = ar.AlarmRuleID
    #         WHERE DateInserted BETWEEN '{dates.getISODate(30)}' AND '{dates.getISODate()}'
    #         AND ar.AlarmType = 5
    #         AND EntityID = 16
    #     """
    #     cursor = self.conn.cursor()
    #     cursor.execute(sql)
    #     rows = cursor.fetchall()
    #     cursor.close()
    #     return rows[0][0]
