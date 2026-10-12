import unittest
from atlas import assets,links,owners,match_assets
from investigate import corroborate,review,similarity
class AtlasInvestigationTests(unittest.TestCase):
 def test_registers_loaded(self):
  self.assertEqual(len(assets()),42)
  self.assertEqual(len(links()),29)
  self.assertEqual(len(owners()),45)
 def test_named_critical_assets(self):
  self.assertEqual(match_assets("Kropotkinskaya CPC pumping station outage")[0]['id'],'CA-001')
  self.assertTrue(any(a['id']=='CA-023' for a in match_assets("KEGOC issued a power grid statement")))
  self.assertTrue(any(a['id']=='CA-032' for a in match_assets("CaspiLink fibre route funding")))
 def test_generic_event_does_not_claim_asset(self):
  self.assertEqual(match_assets("Oil market prices decline amid general economic uncertainty"),[])
 def test_reporting_corroboration(self):
  first={'id':'a','title':'CPC pumping station damaged in Russia - Reuters','source':'Google News Global','sector':'Oil','published':'2026-10-11T15:00:00Z'}
  second={'id':'b','title':'CPC pumping station damaged in Russia - Associated Press','source':'Google News Global','sector':'Oil','published':'2026-10-11T17:00:00Z','url':'https://example.com/report'}
  self.assertEqual(len(corroborate([first,second],first)),1)
 def test_no_automatic_verified_status(self):
  self.assertIsNone(review({'id':'a'},{}))
  self.assertIsNone(review({'id':'a'},{'a':{'reviewer':'X','note':'short','original_source_url':'https://example.com'}}))
 def test_similarity_bounds(self):
  self.assertLess(similarity('Oil export resumes','Concert tour begins'),.25)
if __name__=='__main__':unittest.main()
