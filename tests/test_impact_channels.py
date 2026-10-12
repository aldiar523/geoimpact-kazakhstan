import unittest
from impact_model import decorate,infer_channels,oil_channels
class GeopoliticalChannelTests(unittest.TestCase):
 def test_hormuz_creates_opposing_channels(self):
  e=decorate({'title':'Tanker disruption in Strait of Hormuz sparks global oil price concerns','summary':'Oil supply risk','sector':'Oil','direction':'Unknown'})
  self.assertEqual(e['overall_effect'],'mixed')
  self.assertEqual(e['direction'],'Mixed')
  self.assertEqual(e['country'],'Strait of Hormuz')
  self.assertEqual({x['direction'] for x in e['impact_channels']},{'positive','negative'})
  self.assertTrue(all(x['severity'] is None for x in e['impact_channels']))
  self.assertTrue(all(not x['observed'] for x in e['impact_channels']))
 def test_falling_oil_price_reverses_channel_directions(self):
  e=decorate({'title':'Oil price plunges as demand falls','summary':'Brent crude declines','sector':'Oil','direction':'Unknown'})
  self.assertEqual(e['impact_channels'][0]['direction'],'negative')
  self.assertEqual(e['impact_channels'][1]['direction'],'positive')
 def test_no_fabricated_oil_impact_from_unrelated_event(self):
  e=decorate({'title':'Kazakhstan opens digital government service','summary':'Public service launch','sector':'Digital','direction':'Unknown'})
  self.assertEqual(e['overall_effect'],'unknown')
  self.assertEqual(e['impact_channels'],[])
 def test_hormuz_is_condition_not_factual_effect(self):
  e=decorate({'title':'Oil transit uncertainty in Hormuz','summary':'Price change not quantified','sector':'Oil'})
  self.assertIn('If',e['impact_channels'][0]['condition'])
  self.assertEqual(e['impact_summary'][:3],'Two')
if __name__=='__main__':unittest.main()
