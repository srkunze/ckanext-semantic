import ckan.model.meta as meta
import ckan.model.domain_object as domain_object
import sqlalchemy.types as types


class SimilarityConfiguration(domain_object.DomainObject):
    def __init__(self, entity_uri, similarity_method_uri):
        self.entity_uri = entity_uri
        self.similarity_method_uri = similarity_method_uri
        self.request_count = 0
        self.created = None


similarity_configuration_table = Table(
    'similarity_configuration', meta.metadata,
    Column('entity_uri', types.UnicodeText, nullable=False),
    Column('similarity_method_uri', types.UnicodeText, nullable=False),
    Column('request_count', types.Integer),
    Column('created', types.DateTime)
    )

meta.mapper(SimilarityConfiguration, similarity_configuration_table)
