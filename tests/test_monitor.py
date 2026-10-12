import unittest,monitor
class MonitorTests(unittest.TestCase):
 def test_expected_feeds(self):
  from urllib.parse import unquote
  self.assertEqual(len(monitor.BASE_SOURCES),24)
  self.assertEqual(len(monitor.SOURCES),76)
  self.assertTrue(any('after:' in unquote(x[2]) and 'before:' in unquote(x[2]) for x in monitor.SOURCES))
 def test_asset_match(self):self.assertEqual(monitor.classify('Kropotkinskaya CPC pumping station damaged in Russia','')['sector'],'Oil')
 def test_no_unrelated(self):self.assertIsNone(monitor.classify('Film actor launches clothing line',''))
 def test_probability_not_invented(self):self.assertEqual(monitor.classify('OPEC cuts oil production','')['probability'],'Unassessed')
 def test_generic_sanctions_not_enough(self):self.assertIsNone(monitor.classify('Ukraine sanctions Russian weapons manufacturer','No direct regional connection documented'))
 def test_generic_critical_minerals_not_enough(self):self.assertIsNone(monitor.classify('Korea Zinc US smelter investment and critical minerals',''))
 def test_dates(self):self.assertIsNone(monitor.date('nonsense'))
if __name__=='__main__':unittest.main()
