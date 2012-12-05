import ckanext.semantic.model.dataset_statistics_configuration as dsc
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix

import datetime
import lodstats
import RDF
import sqlalchemy


class DatasetStatistics(StatisticsConcept):
    supported_formats = {
        'application/x-ntriples': 'nt',
        'nt': 'nt',
        'application/x-nquads': 'nq',
        'nquads': 'nq',
        'application/rdf+xml': 'rdf',
        'rdf': 'rdf',
        'text/turtle': 'ttl',
        'rdf/turtle': 'ttl',
        'text/n3': 'n3',
        'n3': 'n3',
        'api/sparql': 'sparql',
        'sparql': 'sparql'
    }

    def __init__(self):
        super(DatasetStatistics, self).__init__()
        self.graph = 'http://lodstats.org/datasets'
        self.dataset = None


    def set_dataset(self, dataset):
        self.dataset = dataset
    

    def create_results(self):
        if not self.dataset:
            self.dataset = self.determine_rdf_dataset_due()

        self.dataset.uri = h.dataset_to_uri(self.dataset.name)
        resource = self._get_rdf_resource(self.dataset)
        format = self._get_resource_format(resource)
        self.results = self._create_results(self.dataset, resource, format)


    def _determine_rdf_dataset_due(self):
        dsc.DatasetStatisticsConfiguration()
        dataset without statistics
        dataset with statistics


    def _get_rdf_resource(self, dataset):
        for resource in dataset.resources:
            if resource.format.lower() in DatasetStatistics.supported_formats.keys():
                return resource
        raise Exception('Given dataset (id=%s) has no RDF resource.' % dataset.id)


    def _get_resource_format(self, resource):
        return DatasetStatistics.supported_formats[resource.format.lower()]


    def _create_results(self, dataset, resource, format):
        dataset_rdf_uri = RDF.Uri(dataset.uri)
        
        results = RDF.Model()
        results.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.evaluated, RDF.Node(literal=datetime.datetime.now().isoformat(), datatype=prefix.xs.dateTime.uri)))

        if resource is None:
            results.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.error, prefix.dstats.NoRDFResource))
            return results

        try:
            rdf_stats = lodstats.RDFStats(format=format, rdfurl=resource.url)
            rdf_stats.parse()
            rdf_stats.do_stats()
            rdf_stats.update_model(dataset_rdf_uri, results)
        except Exception as errorstr:
            results.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.error, prefix.dstats.LODStatsError))
            if isinstance(errorstr, Exception):
                results.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.errorString, RDF.Node(literal=errorstr.message, datatype=prefix.xs.string.uri)))
            else:
                results.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.errorString, RDF.Node(literal=errorstr, datatype=prefix.xs.string.uri)))
        return results


    def update_store(self):
        self.create_results()

        store.root.modify(graph=self.graph,
                          insert_construct=h.rdf_to_string(self.results),
                          delete_construct='?dataset ?predicate ?object.\n?object ?object_predicate ?object_object.',
                          delete_where='?dataset ?predicate ?object.\nfilter(?dataset=<' + self.dataset.uri + '>)')

