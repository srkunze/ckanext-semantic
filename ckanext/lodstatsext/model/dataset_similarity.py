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



vocabulary_specifity_table = Table(
    'dataset_specifity', meta.metadata,
    Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
    Column('dataset_id', types.UnicodeText, nullable=False),
    Column('in_progress', types.Boolean, default=False),
    Column('last_evaluated', types.DateTime),
    Column('error', types.UnicodeText),
    Column('warning_count', types.BigInteger),
    Column('last_warning', types.UnicodeText),
    Column('rdf', types.UnicodeText),
    Column('triple_count', types.BigInteger),
    Column('class_count', types.BigInteger),
    Column('property_count', types.BigInteger),
    Column('vocabulary_count', types.BigInteger),
    )
