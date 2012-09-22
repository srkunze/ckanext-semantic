from sqlalchemy.util import OrderedDict
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import orm, types, Column, Table, ForeignKey
from pylons import config
import vdm.sqlalchemy
import ckan.model.domain_object as domain_object

import ckan.model.meta as meta
from ckan.model.types import make_uuid, JsonDictType
import ckan.model.core as core
from ckan.model.package import *
from ckan.model import extension


dataset_lodstats_table = Table(
    'dataset_lodstats', meta.metadata,
    Column('dataset_id', types.UnicodeText, primary_key=True),
    Column('processing', types.Boolean, default=False),
    Column('last_evaluated', types.DateTime),
    Column('error', types.UnicodeText),
    Column('warning_count', types.BigInteger),
    Column('last_warning', types.UnicodeText),
    Column('rdf', types.UnicodeText),
    Column('triple_count', types.BigInteger),
    Column('class_count', types.BigInteger),
    Column('property_count', types.BigInteger),
    Column('vocabulariy_count', types.BigInteger),
    )

dataset_lodstats_class_partition_table = Table(
    'dataset_lodstats_class_partition', meta.metadata,
    Column('dataset_id', types.UnicodeText, primary_key=True),
    Column('type', types.UnicodeText),
    Column('uri', types.UnicodeText),
    Column('uri_count', types.BigInteger),
    )


vdm.sqlalchemy.make_table_stateful(dataset_lodstats_table)
dataset_lodstats_revision_table = core.make_revisioned_table(dataset_lodstats_table)

vdm.sqlalchemy.make_table_stateful(dataset_lodstats_class_partition_table)
dataset_lodstats_class_partition_revision_table = core.make_revisioned_table(dataset_lodstats_class_partition_table)

class DatasetLODStats(vdm.sqlalchemy.RevisionedObjectMixin,
               vdm.sqlalchemy.StatefulObjectMixin,
               domain_object.DomainObject):
    def __init__(self):
        pass

class DatasetLODStatsClassPartition(vdm.sqlalchemy.RevisionedObjectMixin,
               vdm.sqlalchemy.StatefulObjectMixin,
               domain_object.DomainObject):
    def __init__(self):
        pass


## Mappers

meta.mapper(DatasetLODStats, dataset_lodstats_table,
    order_by=[dataset_lodstats_table.c.dataset_id],
    extension=[vdm.sqlalchemy.Revisioner(dataset_lodstats_revision_table),
               extension.PluginMapperExtension(),
               ],
)

meta.mapper(DatasetLODStatsClassPartition, dataset_lodstats_class_partition_table,
    order_by=[dataset_lodstats_class_partition_table.c.uri],
    extension=[vdm.sqlalchemy.Revisioner(dataset_lodstats_class_partition_revision_table),
               extension.PluginMapperExtension(),
               ],
)

## VDM
    
vdm.sqlalchemy.modify_base_object_mapper(DatasetLODStats, core.Revision, core.State)
DatasetLODStatsRevision = vdm.sqlalchemy.create_object_version(meta.mapper, DatasetLODStats, dataset_lodstats_revision_table)

vdm.sqlalchemy.modify_base_object_mapper(DatasetLODStatsClassPartition, core.Revision, core.State)
DatasetLODStatsClassPartitionRevision = vdm.sqlalchemy.create_object_version(meta.mapper, DatasetLODStatsClassPartition, dataset_lodstats_class_partition_revision_table)

DatasetLODStatsRevision.related_packages = lambda self: [self.continuity.package]
DatasetLODStatsClassPartitionRevision.related_packages = lambda self: [self.continuity.package]

