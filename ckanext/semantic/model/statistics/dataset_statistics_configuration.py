import ckan.model.meta as meta
import ckan.model.domain_object as domain_object
import sqlalchemy


class DatasetStatisticsConfiguration(domain_object.DomainObject):
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.created = None
        self.request_count = 0


dataset_statistics_configuration_table = sqlalchemy.Table(
    'dataset_statistics_configuration', meta.metadata,
    sqlalchemy.Column('dataset_id', sqlalchemy.types.UnicodeText, primary_key=True),
    sqlalchemy.Column('created', sqlalchemy.types.DateTime),
    sqlalchemy.Column('request_count', sqlalchemy.types.Integer)
    )


meta.mapper(DatasetStatisticsConfiguration, dataset_statistics_configuration_table)
