import pylons


class SPARQLClientFactory:
    @classmethod
    def create_client(cls, client_class, role=None):
        if client_class not in SPARQLClient.__subclasses__():
            raise Exception('Given client class is no SPARQL client')
        client = client_class()
        config_name_prefix = 'ckan.semantic.SPARQL'
        for config_name_part in ['username', 'password', 'hostname']:
            config_name = '%s_%s' % (config_name_prefix, config_name_part)
            if role:
                config_name += '_' + role
            config_value = pylons.config.get(config_name)
            getattr(client, 'set_%s' % config_name_part)(config_value)
        endpoints = []
        for index in range(0, 20):
            endpoint = pylons.config.get('ckan.semantic.SPARQL_endpoint%s' % index, None)
            if endpoint:
                endpoints.append(endpoint)
        client.set_endpoints(endpoints)
        return client


class SPARQLClient(object):
    def set_username(self, username):
        self._username = username


    def set_password(self, password):
        self._password = password


    def set_hostname(self, hostname):
        self._hostname = hostname


    def set_port(self, port):
        self._port = port


    def set_endpoints(self, endpoints):
        self._endpoints = endpoints


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


from virtuoso_fedx_client import VirtuosoFedXClient as VFClient
