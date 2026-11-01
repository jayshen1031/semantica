"""Explicit class identity survives property/parent projection, including CamelCase."""
import pytest
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from semantica.ontology import OWLGenerator


@pytest.mark.parametrize('basic',[False,True])
def test_declared_class_iris_are_reused_in_every_reference(basic):
    base='https://example.org/dw/d0#'
    ontology={'uri':base,'name':'D0','version':'1',
        'classes':[{'name':n,'uri':base+n,'label':'Display '+n} for n in ['Order','OrderLine','SpecialOrder']],
        'properties':[{'name':'order','uri':base+'order','type':'object','domain':['OrderLine'],'range':['Order']},
                      {'name':'lineId','uri':base+'lineId','type':'data','domain':['OrderLine'],'range':['xsd:integer']}]}
    ontology['classes'][2]['parent']='Order'
    generator=OWLGenerator()
    turtle=generator._generate_basic(ontology) if basic else generator.generate_owl(ontology,format='turtle')
    graph=Graph().parse(data=turtle,format='turtle')
    assert (URIRef(base+'order'),RDFS.domain,URIRef(base+'OrderLine')) in graph
    assert (URIRef(base+'order'),RDFS.range,URIRef(base+'Order')) in graph
    assert (URIRef(base+'lineId'),RDFS.domain,URIRef(base+'OrderLine')) in graph
    assert (URIRef(base+'lineId'),RDFS.range,XSD.integer) in graph
    assert (URIRef(base+'SpecialOrder'),RDFS.subClassOf,URIRef(base+'Order')) in graph
    declared=set(graph.subjects(RDF.type,OWL.Class))
    assert set(graph.objects(None,RDFS.domain))<=declared
