import unittest
from event_gate import screen,similarity,cluster
class EventScreeningTests(unittest.TestCase):
 def ev(self,title,tier="Systemic-market candidate",sector="Oil",country="Iran",**extra):
  return dict(dict(id=title[:16],title=title,summary="",published="2026-10-10T12:00:00+00:00",
              source="News outlet",url="https://example.org/"+str(len(title)),tier=tier,
              sector=sector,country=country,matches=[]),**extra)
 def test_incident_hormuz_kept(self):
  e=self.ev("Tankers attacked near Strait of Hormuz, oil shipping disrupted")
  self.assertTrue(screen(e)["included"])
 def test_china_export_controls_kept_without_kazakhstan(self):
  e=self.ev("China imposed rare earth export ban",sector="Mining",country="China")
  self.assertTrue(screen(e)["included"])
 def test_pipeline_asset_outage_kept(self):
  e=self.ev("CPC pipeline shutdown in Russia",tier="Named asset match",country="Russia",matches=[{"asset_id":"CA-001"}])
  self.assertTrue(screen(e)["included"])
 def test_in_force_trade_agreement_kept(self):
  e=self.ev("EAEU–UAE trade agreement entered into force",tier="Kazakhstan mentioned",sector="Trade",country="United Arab Emirates")
  self.assertTrue(screen(e)["included"])
 def test_editorial_excluded(self):
  e=self.ev("Analysis: Why Kazakhstan's oil logistics trap matters",tier="Kazakhstan mentioned",country="Kazakhstan")
  self.assertFalse(screen(e)["included"])
 def test_forecast_not_event(self):
  e=self.ev("Experts forecast Brent could reach $150 amid Hormuz fears")
  self.assertFalse(screen(e)["included"])
 def test_generic_diplomatic_discussion_not_event(self):
  e=self.ev("Kazakhstan and Germany discuss industrial cooperation",tier="Kazakhstan mentioned",country="Germany",sector="Mining")
  self.assertFalse(screen(e)["included"])
 def test_pure_price_explainer_not_event(self):
  e=self.ev("Explainer: What is OPEC and why does it affect oil prices?")
  self.assertFalse(screen(e)["included"])
 def test_global_real_oil_price_change(self):
  e=self.ev("Brent crude oil prices surged after major shipping outage")
  self.assertTrue(screen(e)["included"])
 def test_dedup_same_story(self):
  e=self.ev("Tankers attacked near Strait of Hormuz, oil shipping disrupted")
  x=dict(e,id="second",title="Tankers attacked near Strait of Hormuz, oil shipping disrupted - Reuters",
         source="Reuters",url="https://other.org/story")
  a,b=({**e,"triage":screen(e)},{**x,"triage":screen(x)})
  c=cluster([a,b])
  self.assertEqual(len(c),1)
  self.assertEqual(c[0]["article_count"],2)
  self.assertEqual(len(c[0]["related_sources"]),2)
 def test_distinct_shocks_not_merged(self):
  a=self.ev("Oil pipeline attacked near Novorossiysk",country="Russia")
  b=dict(self.ev("Oil terminal closed after fire in Black Sea",country="Russia"),
         published="2026-10-01T12:00:00+00:00")
  self.assertEqual(len(cluster([{**a,"triage":screen(a)},{**b,"triage":screen(b)}])),2)
 def test_material_oil_shipments_rise(self):
  e=self.ev("KazTransOil’s oil shipments via BTC rise 24% to 1.164M tons",tier="Named asset match",country="Kazakhstan",matches=[{"asset_id":"CA-003"}])
  self.assertTrue(screen(e)["included"],screen(e))
 def test_named_uranium_approval(self):
  e=self.ev("Kazatomprom shareholders approve China uranium sale",tier="Named asset match",sector="Mining",country="Kazakhstan",matches=[{"asset_id":"CA-011"}])
  self.assertTrue(screen(e)["included"],screen(e))
 def test_tanker_incidents_grouped_as_situation(self):
  first=self.ev("Two oil tankers attacked near Strait of Hormuz",country="Strait of Hormuz")
  second=self.ev("Seven vessels hit by projectiles in Strait of Hormuz",country="Strait of Hormuz")
  first['id']='t1';second['id']='t2'
  self.assertEqual(len(cluster([{**first,"triage":screen(first)},{**second,"triage":screen(second)}])),1)
 def test_explanatory_article_with_actual_decision(self):
  e=self.ev("China Tightens Car Export Rules - Will It Affect Kazakhstan?",tier="Kazakhstan mentioned",sector="Trade",country="China")
  self.assertTrue(screen(e)["included"],screen(e))
 def test_promo_infrastructure_upgrades_not_event(self):
  e=self.ev("Kazakhstan Bridges Distances With Major Transport Upgrades",tier="Kazakhstan mentioned",sector="Transport",country="Kazakhstan")
  self.assertFalse(screen(e)["included"],screen(e))
 def test_cross_border_water_allocation_agreement(self):
  e=self.ev("Kazakhstan and Central Asian States Agree Water Allocation for 2026-2027",tier="Kazakhstan mentioned",sector="Water",country="Uzbekistan")
  self.assertTrue(screen(e)["included"],screen(e))
 def test_unrelated_news_not_risk(self):
  e=self.ev("New fashion collection launches in London",tier="Kazakhstan mentioned")
  self.assertFalse(screen(e)["included"])
if __name__=="__main__":unittest.main()
