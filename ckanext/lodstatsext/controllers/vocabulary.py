import ckan.lib.base as base
import logging
import virtuoso.endpoint as endpoint
import requests
import xml.dom.minidom as dom_parser
import json

log = logging.getLogger(__name__)


class VocabularyController(base.BaseController):
    def read(self, query=None):
        x = []

        r = requests.get('http://lov.okfn.org/endpoint/lov?query=SELECT+%3Ftitle+%3Fprefix+%3Fvocabulary%0D%0AWHERE%0D%0A{%0D%0A++++%3Fvocabulary+a+<http%3A%2F%2Fpurl.org%2Fvocommons%2Fvoaf%23Vocabulary>.%0D%0A++++%3Fvocabulary+<http%3A%2F%2Fpurl.org%2Fvocab%2Fvann%2FpreferredNamespacePrefix>+%3Fprefix.%0D%0A++++%3Fvocabulary+<http%3A%2F%2Fpurl.org%2Fdc%2Fterms%2Ftitle>+%3Ftitle.%0D%0A}&format=SPARQL')
        result = dom_parser.parseString(r.text.encode('utf-8'))
        rows = result.getElementsByTagName('result')
        for row in rows:
            bindings = row.getElementsByTagName('binding')
            y = {}
            x.append(y)
            for binding in bindings:
                for type_ in ['literal', 'uri', 'bnode']:
                    z = binding.getElementsByTagName(type_)
                    if z.length == 1:
                        y[binding.getAttribute('name')] = z.item(0).firstChild.data
                        break


        return json.dumps(x)
        
