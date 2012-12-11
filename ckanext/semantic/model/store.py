import virtuoso.virtuoso as virtuoso


root = virtuoso.Virtuoso('localhost', 'dba', 'dba', 8890, '/sparql')
user = virtuoso.Virtuoso('localhost', 'dba', 'dba', 8890, '/sparql') #user with read-only rights


