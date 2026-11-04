"""SHACL text and regex literals survive Turtle serialization unchanged."""
from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import XSD

from semantica.ontology import SHACLGenerator, run_shacl_validation


def test_shacl_quoted_provenance_and_regex_round_trip():
    ns = Namespace('https://example.org/literal/')
    sh = Namespace('http://www.w3.org/ns/shacl#')
    label = 'Quoted "name"\\path\n第二行'
    description = 'source quote=\\"No\\"; path=C:\\docs\n\t出处'
    pattern = r'^P\d{7}$'
    candidate = {'uri': str(ns), 'classes': [
        {'name': 'Process', 'uri': str(ns.Process), 'label': label, 'comment': description}],
        'properties': [{'name': 'displayId', 'uri': str(ns.displayId), 'type': 'data',
                        'domain': ['Process'], 'range': ['xsd:string'], 'pattern': pattern}]}
    generator = SHACLGenerator(quality_tier='standard')
    shapes = generator.serialize(generator.generate(candidate), 'turtle')
    graph = Graph().parse(data=shapes, format='turtle')
    node = next(graph.subjects(sh.targetClass, ns.Process))
    assert graph.value(node, sh.name) == Literal(label)
    assert graph.value(node, sh.description) == Literal(description)
    prop = next(graph.objects(node, sh.property))
    assert graph.value(prop, sh.pattern) == Literal(pattern)
    for value, conforms in [('P1234567', True), ('P123', False)]:
        data = Graph()
        data.add((ns.example, RDF.type, ns.Process))
        data.add((ns.example, ns.displayId, Literal(value, datatype=XSD.string)))
        assert run_shacl_validation(data.serialize(format='turtle'), shapes).conforms is conforms
