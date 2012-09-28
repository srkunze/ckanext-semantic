import sqlalchemy
import sqlalchemy.types as types
import ckan.model as model
import ckan.model.domain_object as domain_object
import ckan.model.core as core
import ckan.model.meta as meta
import ckan.model.types as ckan_types
import vdm.sqlalchemy


dataset_lodstats_table = sqlalchemy.Table(
    'dataset_lodstats', meta.metadata,
    sqlalchemy.Column('id', types.UnicodeText, primary_key=True, default=ckan_types.make_uuid),
    sqlalchemy.Column('dataset_id', types.UnicodeText, nullable=False),
    sqlalchemy.Column('in_progress', types.Boolean, default=False),
    sqlalchemy.Column('last_evaluated', types.DateTime),
    sqlalchemy.Column('error', types.UnicodeText),
    sqlalchemy.Column('warning_count', types.BigInteger),
    sqlalchemy.Column('last_warning', types.UnicodeText),
    sqlalchemy.Column('rdf', types.UnicodeText),
    sqlalchemy.Column('triple_count', types.BigInteger),
    sqlalchemy.Column('class_count', types.BigInteger),
    sqlalchemy.Column('property_count', types.BigInteger),
    sqlalchemy.Column('vocabulary_count', types.BigInteger),
    )

dataset_lodstats_partition_table = sqlalchemy.Table(
    'dataset_lodstats_partition', meta.metadata,
    sqlalchemy.Column('id', types.UnicodeText, primary_key=True, default=ckan_types.make_uuid),
    sqlalchemy.Column('dataset_lodstats_id', types.UnicodeText, nullable=False),
    sqlalchemy.Column('type', types.UnicodeText, nullable=False),
    sqlalchemy.Column('uri', types.UnicodeText, nullable=False),
    sqlalchemy.Column('uri_count', types.BigInteger, nullable=False),
    )


vdm.sqlalchemy.make_table_stateful(dataset_lodstats_table)
dataset_lodstats_revision_table = core.make_revisioned_table(dataset_lodstats_table)

vdm.sqlalchemy.make_table_stateful(dataset_lodstats_partition_table)
dataset_lodstats_partition_revision_table = core.make_revisioned_table(dataset_lodstats_partition_table)


class DatasetLODStats(vdm.sqlalchemy.RevisionedObjectMixin,
               vdm.sqlalchemy.StatefulObjectMixin,
               domain_object.DomainObject):
    def __init__(self):
        pass

class DatasetLODStatsPartition(vdm.sqlalchemy.RevisionedObjectMixin,
               vdm.sqlalchemy.StatefulObjectMixin,
               domain_object.DomainObject):
    def __init__(self, type_):
        self.type = type_


meta.mapper(DatasetLODStats, dataset_lodstats_table,
    order_by=[dataset_lodstats_table.c.dataset_id],
    extension=[vdm.sqlalchemy.Revisioner(dataset_lodstats_revision_table),
               model.extension.PluginMapperExtension(),
               ],
)

meta.mapper(DatasetLODStatsPartition, dataset_lodstats_partition_table,
    order_by=[dataset_lodstats_partition_table.c.uri],
    extension=[vdm.sqlalchemy.Revisioner(dataset_lodstats_partition_revision_table),
               model.extension.PluginMapperExtension(),
               ],
)


vdm.sqlalchemy.modify_base_object_mapper(DatasetLODStats, core.Revision, core.State)
DatasetLODStatsRevision = vdm.sqlalchemy.create_object_version(meta.mapper, DatasetLODStats, dataset_lodstats_revision_table)

vdm.sqlalchemy.modify_base_object_mapper(DatasetLODStatsPartition, core.Revision, core.State)
DatasetLODStatsPartitionRevision = vdm.sqlalchemy.create_object_version(meta.mapper, DatasetLODStatsPartition, dataset_lodstats_partition_revision_table)

