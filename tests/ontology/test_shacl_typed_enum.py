"""Typed enum members must match valid data and still reject other values."""
import pytest
from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD
from semantica.ontology import SHACLGenerator, run_shacl_validation


@pytest.mark.parametrize('datatype,allowed,invalid', [
    ('string', ['completed', 'a"b\\c\n'], 'pending'),
    ('integer', [1, 2], 3),
    ('boolean', [True], False),
])
def test_turtle_enum_retains_declared_datatype(datatype, allowed, invalid):
    ns=Namespace('https://example.org/enum/')
    candidate={'uri':str(ns), 'classes':[{'name':'Order','uri':str(ns.Order)}],
        'properties':[{'name':'status','uri':str(ns.status),'type':'data','domain':['Order'],
            'range':['xsd:'+datatype],'required':True,'enum':allowed}]}
    generator=SHACLGenerator(quality_tier='strict')
    shapes=generator.serialize(generator.generate(candidate),'turtle')
    Graph().parse(data=shapes,format='turtle')
    for value in [*allowed,invalid]:
        data=Graph();data.add((ns.example,RDF.type,ns.Order))
        data.add((ns.example,ns.status,Literal(value,datatype=XSD[datatype])))
        result=run_shacl_validation(data.serialize(format='turtle'),shapes)
        assert result.conforms is (value in allowed)
