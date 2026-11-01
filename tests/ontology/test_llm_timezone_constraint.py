"""Normalization and SHACL preserve source-required UTC/aware timestamp checks."""
from rdflib import Graph, Namespace, RDF, Literal
from rdflib.namespace import XSD
from semantica.ontology import SHACLGenerator, run_shacl_validation
from semantica.ontology.llm_generator import LLMOntologyGenerator


def test_pattern_survives_llm_normalization_and_rejects_naive_or_non_utc_time():
    ns=Namespace('https://example.org/time/')
    raw={'classes':[{'name':'Order','uri':str(ns.Order)}], 'properties':[
        {'name':'ordered_at','uri':str(ns.ordered_at),'type':'data','domain':['Order'],'range':['xsd:dateTime'],
         'required':True,'cardinality':{'min':1,'max':1},'pattern':'(Z|[+]00:00)$'}]}
    generator=object.__new__(LLMOntologyGenerator);generator.provider_name='synthetic-no-model'
    model=generator._normalize_output(raw,base_uri=str(ns))
    assert model['properties'][0]['pattern']==raw['properties'][0]['pattern']
    shacl=SHACLGenerator(quality_tier='strict');shapes=shacl.serialize(shacl.generate(model),'turtle')
    for text,expected in [('2026-01-01T00:00:00Z',True),('2026-01-01T00:00:00.000001+00:00',True),
                          ('2026-01-01T00:00:00',False),('2026-01-01T00:00:00+01:00',False)]:
        data=Graph();data.add((ns.example,RDF.type,ns.Order));data.add((ns.example,ns.ordered_at,Literal(text,datatype=XSD.dateTime)))
        assert run_shacl_validation(data.serialize(format='turtle'),shapes).conforms is expected
