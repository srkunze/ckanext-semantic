import tempfile
import subprocess


class VirtuosoClient(SPARQLClient):
    def query(self, query_string):
    '''
    '''


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


    def clear_graph(self, graph):
        return self._query_ISQL("CLEAR GRAPH <%s>" % self._graph)


    def _query_ISQL(self, query):
        query = 'SPARQL %s;' % query

        temporary_file = tempfile.NamedTemporaryFile()
        temporary_file.write(cmd)
        temporary_file.flush()

        cmd = ["isql-v", self.hostname, self.username, self.password, temporary_file.name]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            raise ISQLException(err)

        temporary_file.close()

        return out


class ISQLException(Exception):
    pass
