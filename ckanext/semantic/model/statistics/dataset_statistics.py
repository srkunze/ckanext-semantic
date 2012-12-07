from . import StatisticsConcept
import dataset_statistics_configuration as dsc
import ckanext.semantic.lib.helpers as h
import ckanext.semantic.model.prefix as prefix
import datetime
import lodstats
import RDF
import sqlalchemy


class DatasetStatistics(StatisticsConcept):
    _supported_formats = {
        'application/x-ntriples': 'nt',
        'nt': 'nt',
        'application/x-nquads': 'nq',
        'nquads': 'nq',
        'nq': 'nq',
        'application/rdf+xml': 'rdf',
        'rdf': 'rdf',
        'text/turtle': 'ttl',
        'rdf/turtle': 'ttl',
        'ttl': 'ttl',
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


    def set_waiting_time(self, waiting_time):
        self._waiting_time = int(waiting_time)


    def set_ratio_old_new(self, ratio_old_new):
        self._ratio_old_new = float(ratio_old_new)


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
        now = datetime.datetime.now()
        rdf_dataset_query = self._get_rdf_dataset_query()
        configuration_subquery = self._get_configurations_subquery()

        query = rdf_dataset_query.filter(~ self._model.Package.id.in_(configuration_subquery))
        query = query.join(self._model.PackageRevision, self._model.PackageRevision.continuity_id==self._model.Package.id)
        query = query.add_column(sqlalchemy.func.min(self._model.PackageRevision.revision_timestamp)).group_by(self._model.Package.id)

        id_without, q_without = self._get_oldest_dataset(query, now)

        query = rdf_dataset_query.filter(self._model.Package.id.in_(configuration_subquery))
        query = query.join(dsc.DatasetStatisticsConfiguration, self._model.Package.id==dsc.DatasetStatisticsConfiguration.dataset_id)
        query = query.filter(dsc.DatasetStatisticsConfiguration.created < (datetime.datetime.now() - datetime.timedelta(weeks=self._waiting_time)))
        query = query.add_column(dsc.DatasetStatisticsConfiguration.created)
        query = query.order_by(dsc.DatasetStatisticsConfiguration.created)
        result = query.first()
        id_with = None
        q_with = 0
        if result:
            id_with = result[0]
            q_with = self._ratio_old_new * float(((now - result[1]) - datetime.timedelta(weeks=self._waiting_time)).days)

        dataset_id_due = id_without
        if q_with > q_without:
            dataset_id_due = id_with

        if dataset_id_due:
            return self._session.query(self._model.Package).get(dataset_id_due)


    def _get_rdf_dataset_query(self):
        rdf_dataset_query = self._session.query(self._model.Package.id)
        rdf_dataset_query = rdf_dataset_query.join(self._model.ResourceGroup, self._model.ResourceGroup.package_id==self._model.Package.id)
        rdf_dataset_query = rdf_dataset_query.join(self._model.Resource, self._model.Resource.resource_group_id==self._model.ResourceGroup.id)
        rdf_dataset_query = rdf_dataset_query.filter(self._model.Resource.format.in_(DatasetStatistics._supported_formats.keys()))
        return rdf_dataset_query


    def _get_configurations_subquery(self):
        return self._session.query(dsc.DatasetStatisticsConfiguration.dataset_id).subquery('configuration')


    def _get_oldest_dataset(self, query, now):
        id = None
        timestamp = now
        for row in query.all():
            if row[1] < timestamp:
                id = row[0]
                timestamp = row[1]
        return id, float((now - timestamp).days)


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
            results.append(RDF.Statement(dataset_rdf_uri, prefix.dstats.error, prefix.dstats.StatisticToolError))
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

