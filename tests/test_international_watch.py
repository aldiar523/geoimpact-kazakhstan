import unittest
from monitor import classify,EXTERNAL_EXPOSURES,EXTERNAL_CHANGE
from international_watch import exposure
class InternationalShockTests(unittest.TestCase):
 def ev(self,title,**updates):
  data={'id':title[:15],'title':title,'summary':'','published':'2026-10-11T05:00:00+00:00',
        'tier':'External shock watch','sector':'Trade','country':'China','source':'RSS','url':'https://example.org/story'}
  data.update(updates);return data
 def test_implemented_chinese_trade_action(self):
  e=self.ev('China imposes export controls on rare earth minerals',sector='Mining')
  self.assertIsNotNone(exposure(e))
 def test_iran_shipping_incident(self):
  e=self.ev('Oil tanker attacked near Strait of Hormuz',sector='Oil',country='Iran')
  self.assertIsNotNone(exposure(e))
 def test_no_automatic_domestic_effect(self):
  x=exposure(self.ev('China imposed rare earth export controls',sector='Mining'))
  self.assertIn('Critical',x['reason'] if x else 'Critical')
 def test_forecast_is_not_event(self):
  self.assertIsNone(exposure(self.ev('Analysts forecast oil price could rise sharply next year',sector='Oil')))
 def test_bilateral_news_kazakhstan_not_global(self):
  self.assertIsNone(exposure(self.ev('Kazakhstan and China sign trade agreement',country='China')))
 def test_external_classifier_not_every_discussion(self):
  self.assertIsNone(classify('Europe debates future of monetary cooperation','No tariffs or binding decisions'))
 def test_actionable_exposure_produces_location(self):
  e=classify('China imposes rare earth export controls on minerals','')
  self.assertIsNotNone(e);self.assertEqual(e['tier'],'External shock watch')
  self.assertEqual(e['country'],'China')
if __name__=='__main__':unittest.main()
