import ckan.model.meta as meta
import ckan.model.domain_object as domain_object
import sqlalchemy


class SimilarityConfiguration(domain_object.DomainObject):
    def __init__(self, entity_uri, similarity_method_uri):
        self.entity_uri = entity_uri
        self.similarity_method_uri = similarity_method_uri
        self.created = None
        self.request_count = 0


similarity_configuration_table = sqlalchemy.Table(
    'similarity_configuration', meta.metadata,
    sqlalchemy.Column('entity_uri', sqlalchemy.types.UnicodeText, primary_key=True),
    sqlalchemy.Column('similarity_method_uri', sqlalchemy.types.UnicodeText, primary_key=True),
    sqlalchemy.Column('created', sqlalchemy.types.DateTime),
    sqlalchemy.Column('request_count', sqlalchemy.types.Integer)
    )


meta.mapper(SimilarityConfiguration, similarity_configuration_table)
