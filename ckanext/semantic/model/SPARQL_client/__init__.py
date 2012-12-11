class SPARQLClient:
    def set_username(self, username):
        self._username = username


    def set_password(self, password):
        self._password = password


    def set_url(self, url):
        self._url = url


    def set_graph(self, graph):
        self._graph = graph


    def query(self, query_string):
    '''
        Use SPARQL to query the given graph.
    '''

    def modify(self, insert_construct=None, insert_where=None, delete_construct=None, delete_where=None):
    '''
        Use SPARQL Update to modify the given graph.
    '''

    def clear_graph(self):
    '''
        Clear the given graph.
    '''
