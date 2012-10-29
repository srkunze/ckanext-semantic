import virtuoso.virtuoso as virtuoso


root = virtuoso.Virtuoso('localhost', 'dba', 'dba', 8890, '/sparql')
user = virtuoso.Virtuoso('localhost', 'dba', 'dba', 8890, '/sparql') #user with read-only rights

#print ts.modify('INSERT IN GRAPH <http://lodstats.org/> { <http://x.com#x> <http://x.com#y> "Juan" }')
#print ts.query('select * WHERE { ?s ?p ?o filter (?s = <http://x.com#x>) }', 'json')
#print ts.modify('delete from <http://lodstats.org/> { ?s ?p ?o } where { ?s ?p ?o filter (?s = <http://x.com#x>) }')

