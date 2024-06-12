import unittest
import pandas as pd
from datetime import datetime, date, timedelta
from modules.database import MSQLServer  # Asegúrate de ajustar el nombre del módulo

class TestMSQLServer(unittest.TestCase):

    def setUp(self):
        self.msql_server = MSQLServer()
        # Usar menos Entity IDs
        entity_ids = pd.DataFrame({'EntityID': [4]})
        self.msql_server.set_entity_ids(entity_ids)

        # Configurar el rango de fechas desde hoy hasta hace 5 días
        end_date = date.today()
        start_date = end_date - timedelta(days=5)
        self.msql_server.set_date_range((start_date, end_date))
    
    def test_set_entity_ids(self):
        entity_ids = pd.DataFrame({'EntityID': [1, 2, 3]})
        self.msql_server.set_entity_ids(entity_ids)
        self.assertIsNotNone(self.msql_server._entity_ids)
        self.assertTrue(isinstance(self.msql_server._entity_ids, pd.DataFrame))
    
    def test_set_entity_ids_invalid(self):
        with self.assertRaises(ValueError):
            self.msql_server.set_entity_ids("invalid data")
    
    def test_set_date_range(self):
        end_date = date.today()
        start_date = end_date - timedelta(days=5)
        start_str, end_str = self.msql_server.set_date_range((start_date, end_date))
        self.assertEqual(start_str, (start_date.strftime('%Y-%m-%dT00:00:00Z')))
        self.assertEqual(end_str, (end_date.strftime('%Y-%m-%dT23:59:59Z')))
    
    def test_get_entities(self):
        result = self.msql_server.get_entities()
        print(result)
        self.assertGreater(len(result), 0)
        self.assertIn('EntityID', result.columns)
        self.assertIn('Name', result.columns)

    def test_get_alarm_count(self):
        count = self.msql_server.get_alarm_count()
        print(f"Alarm Count: {count}")
        self.assertGreaterEqual(count, 0)

    def test_get_alarm_summary_by_entity_and_status(self):
        result = self.msql_server.get_alarm_summary_by_entity_and_status()
        print(result)
        self.assertGreater(len(result), 0)
        self.assertIn('EntityName', result.columns)
        self.assertIn('AlarmStatus', result.columns)
        self.assertIn('AlarmCount', result.columns)

    def test_get_alarm_details_by_entity(self):
        result = self.msql_server.get_alarm_details_by_entity()
        print(result)
        self.assertGreater(len(result), 0)
        self.assertIn('Entity Name', result.columns)
        self.assertIn('Alarm Date', result.columns)
        self.assertIn('Alarm ID', result.columns)
        self.assertIn('Alarm Name', result.columns)
        self.assertIn('Alarm Status', result.columns)

    def test_get_full_alarm_details(self):
        result = self.msql_server.get_full_alarm_details()
        print(result)
        self.assertGreater(len(result), 0)
        self.assertIn('EntityID', result.columns)
        self.assertIn('AlarmDate', result.columns)
        self.assertIn('AlarmStatus', result.columns)

    def test_get_alarm_durations(self):
        result = self.msql_server.get_alarm_durations()
        print(result)
        self.assertGreater(len(result), 0)
        self.assertIn('EntityID', result.columns)
        self.assertIn('TTD', result.columns)
        self.assertIn('TTR', result.columns)
