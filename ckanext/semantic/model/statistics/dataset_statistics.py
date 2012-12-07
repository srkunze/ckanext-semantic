from . import StatisticsConcept
import dataset_statistics_configuration as dsc
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix
import datetime
import lodstats
import RDF


class DatasetStatistics(StatisticsConcept):
    _supported_formats = {
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
        self._graph = 'http://stats.lod2.eu/datasets'
        self._dataset = None


    def set_dataset(self, dataset):
        self._dataset = dataset


    def set_quiescent_time(self, quiescent_time):
        self._quiescent_time = int(quiescent_time)


    def create_results(self):
        if not self._dataset:
            self._dataset = self._determine_rdf_dataset_due()
            if not self._dataset:
                return

        configuration = self._get_configuration()
        configuration.created = datetime.datetime.now()
        self._session.merge(configuration)
        self._session.commit()

        print "dataset statistics for %s (%s) created at %s" % (self._dataset.id, self._dataset.name, configuration.created.isoformat())

        self._dataset.uri = h.dataset_to_uri(self._dataset.name)
        resource = self._get_rdf_resource(self._dataset)
        format = self._get_resource_format(resource)
        self.results = self._create_results(self._dataset, resource, format)


    def _determine_rdf_dataset_due(self):
        configurations = self._session.query(dsc.DatasetStatisticsConfiguration.dataset_id).subquery('configurations')
        dataset_query = self._session.query(self._model.Package)

        query = dataset_query.filter(~ self._model.Package.id.in_(configurations))
        query = query.join(self._model.Revision, self._model.Package.revision_id==self._model.Revision.id)
        query = query.order_by(self._model.Revision.timestamp)
        datasets_without_statistics = query.all()

        dataset = self._first_rdf_dataset(datasets_without_statistics)
        if dataset:
            return dataset

        query = dataset_query.join(dsc.DatasetStatisticsConfiguration, self._model.Package.id==dsc.DatasetStatisticsConfiguration.dataset_id)
        query = query.filter(dsc.DatasetStatisticsConfiguration.created < (datetime.datetime.now() - datetime.timedelta(weeks=self._quiescent_time)))
        query = query.order_by(dsc.DatasetStatisticsConfiguration.created)
        datasets_with_statistics = query.all()
        return self._first_rdf_dataset(datasets_with_statistics)


    def _first_rdf_dataset(self, datasets):
        for dataset in datasets:
            if self._is_rdf_dataset(dataset):
                return dataset


    def _is_rdf_dataset(self, dataset):
        try:
            self._get_rdf_resource(dataset)
        except Exception:
            return False
        return True


    def _get_rdf_resource(self, dataset):
        for resource in dataset.resources:
            if resource.format.lower() in DatasetStatistics._supported_formats.keys():
                return resource
        raise Exception('Given dataset (id=%s) has no RDF resource.' % dataset.id)


    def _get_resource_format(self, resource):
        return DatasetStatistics._supported_formats[resource.format.lower()]


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
        if not self._dataset:
            return

        self._store.modify(graph=self._graph,
                          insert_construct=h.rdf_to_string(self.results),
                          delete_construct='?dataset ?predicate ?object.\n?object ?object_predicate ?object_object.',
                          delete_where='?dataset ?predicate ?object.\nfilter(?dataset=<' + self._dataset.uri + '>)')
        print "store update at %s" % datetime.datetime.now().isoformat()


    def _get_configuration(self):
        configuration = self._model.Session.query(dsc.DatasetStatisticsConfiguration).get(self._dataset.id)
        if not configuration:
            configuration = dsc.DatasetStatisticsConfiguration(self._dataset.id)
        return configuration

