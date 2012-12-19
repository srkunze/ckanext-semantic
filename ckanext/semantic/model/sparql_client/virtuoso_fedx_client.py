from . import SPARQLClient
import requests
import json
import re
import pylons
import subprocess
import tempfile
import urllib
import uuid
import shutil


class VirtuosoFedXClient(SPARQLClient):
    def query(self, query_string):
        try:
            return self._query(query_string)
        except SPARQLError as error:
            return error


    def query_bindings_only(self, query_string):
        try:
            return self._query(query_string)['results']['bindings']
        except SPARQLError as error:
            return error


    def query_value(self, query_string, datatype=str):
        try:
            results = self._query(query_string)
            return datatype(results['results']['bindings'][0].values()[0]['value'])
        except SPARQLError as error:
            return error


    def query_list(self, query_string, datatypes):
        try:
            results = []
            for binding in self._query(query_string)['results']['bindings']:
                result = {}
                for name, datatype in datatypes.iteritems():
                    if name in binding:
                        result[name] = datatype(binding[name]['value'])
                if result:
                    results.append(result)
            return results
        except SPARQLError as error:
            return error


    def _query(self, query_string):
        if not self._endpoints:
            return {'head': {'vars': []}, 'results': {'bindings': []}}

        if len(self._endpoints) == 1:
            url = '%s?query=%s' % (self._endpoints[0], urllib.quote(query_string))
            response = requests.get(url, headers={'Accept': 'application/sparql-results+json, application/sparql-results+xml'})
            try:
                return json.loads(response.text)
            except:
                raise SPARQLError(response.text)
        
        query_string = query_string.replace('\n', ' ')
        folder = str(uuid.uuid1())
        
        command = ['java', '-cp', 'bin:%s' % pylons.config.get('ckan.semantic.FedX'), 'com.fluidops.fedx.CLI']
        for endpoint in self._endpoints:
            command.append('-s')
            command.append(endpoint)
        command = command + ['-f', 'JSON', '-folder', folder, '-q', query_string]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        try:
            json_data=open('results/%s/q_1.json' % folder, 'r')
            data = json.load(json_data)
            json_data.close()
            shutil.rmtree('results/%s' % folder)
            return data
        except:
            raise SPARQLError(out)


    def modify(self, insert_construct=None, insert_where=None, delete_construct=None, delete_where=None):
        if self._graph is not None:
            from_graph_query = ' from <' + self._graph + '>'
            into_graph_query = ' into <' + self._graph + '>'
        else:
            from_graph_query = ''
            into_graph_query = ''
        
        delete_query = ''
        if delete_construct:
            delete_query = 'delete' + from_graph_query + '\n{' + delete_construct + '\n}\n'
        if delete_where:
            delete_query += 'where\n{' + delete_where + '\n}\n'
            
        insert_query = ''
        if insert_construct:
            insert_query = 'insert' + into_graph_query + '\n{' + insert_construct + '\n}\n'
        if insert_where:
            insert_query += 'where\n{' + insert_where + '\n}\n'

        query = delete_query + '\n' + insert_query

        return self._query_ISQL(query)


    def clear_graph(self):
        return self._query_ISQL('CLEAR GRAPH <%s>' % self._graph)


    def _query_ISQL(self, query):
        temporary_file = tempfile.NamedTemporaryFile()
        temporary_file.write('SPARQL %s;' % query)
        temporary_file.flush()
        
        command = ['isql-v', self._hostname, self._username, self._password, temporary_file.name]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            raise ISQLException(err)

        temporary_file.close()

        return out


class ISQLException(Exception):
    pass

class SPARQLError(Exception):
    pass
