"""Read dated Atlas research observations; do not infer impacts from asset mentions."""
import csv,re
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ALIASES={
'CA-001':'caspian pipeline consortium|cpc pipeline|cpc pumping|kropotkinskaya|cpc terminal',
'CA-002':'novorossiysk cpc|cpc marine terminal|cpc terminal|novorossiysk oil terminal',
'CA-003':'kaztransoil','CA-004':'atyrau samara|atyrau–samara',
'CA-005':'atasu alashankou|kazakhstan china pipeline|kenkiyak kumkol',
'CA-006':'munaitas','CA-007':'aktau port|aktau oil terminal|trans caspian oil',
'CA-008':'tengizchevroil|tengiz oilfield|tengiz field',
'CA-009':'kashagan|north caspian project','CA-010':'karachaganak',
'CA-011':'kazatomprom','CA-012':'jv inkai|inkai uranium|inkai mine',
'CA-013':'katco|tortkuduk|muyunkum','CA-014':'mc ortalyk',
'CA-015':'budenovskoye|budenovskoe','CA-016':'ulba metallurgical|ulba metallurgy',
'CA-017':'skz-u|taiqonyr|sulphuric acid shortage kazakhstan',
'CA-018':'kazzinc','CA-019':'kazchrome|eurasian resources group|erg kazakhstan',
'CA-020':'aktogay','CA-021':'bozshakol','CA-022':'balkhash smelter',
'CA-023':'kegoc|kazakhstan national grid',
'CA-024':'russia kazakhstan electricity|russia kazakhstan power grid',
'CA-025':'central asian power grid|uzbekistan kazakhstan grid|central asian electricity network',
'CA-026':'north south power corridor kazakhstan|north-south transmission kazakhstan',
'CA-027':'western kazakhstan grid integration',
'CA-028':'southern kazakhstan grid reinforcement',
'CA-029':'kazakhstan internet gateway|kazakhstan cross-border fibre|kazakhstan fiber transit',
'CA-030':'kazakhtelecom','CA-031':'transtelecom kazakhstan',
'CA-032':'caspilink|trans-caspian fiber|trans-caspian fibre|digital silk way',
'CA-033':'kaz-gov-ix',
'CA-034':'kazakhstan cloud dependency|kazakhstan dns infrastructure',
'CA-035':'ili river|lake balkhash|kapshagay reservoir|qapshaghay',
'CA-036':'irtysh river|ertis river|irtysh transboundary',
'CA-037':'ural river kazakhstan|zhaiyk river|zhaik river',
'CA-038':'syr darya|syrdarya|shardara reservoir',
'CA-039':'chu river|orto tokoy|orto-tokoy',
'CA-040':'talas river|kirov reservoir kyrgyz',
'CA-041':'emel river kazakhstan',
'CA-042':'china kazakhstan water commission|china kazakhstan water treaty'
}
def read_records(filename):
 with (ROOT/'data'/filename).open(encoding='utf-8-sig',newline='') as fh:
  return list(csv.DictReader(fh,delimiter='|'))
@lru_cache(maxsize=1)
def assets():return read_records('atlas_assets.psv')
@lru_cache(maxsize=1)
def owners():return read_records('atlas_ownership.psv')
@lru_cache(maxsize=1)
def links():return read_records('atlas_links.psv')
def match_assets(text):
 lower=text.lower();found=[]
 for a in assets():
  terms=ALIASES.get(a['id'],'').split('|')
  if any(term and re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',lower) for term in terms):
   found.append({k:a[k] for k in ('id','name','sector','external_counterpart','source_url')})
 return found
