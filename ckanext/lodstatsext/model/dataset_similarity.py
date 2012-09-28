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
    'vocabulary_specifity', meta.metadata,
    Column('vocabulary', types.UnicodeText, primary_key=True),
    Column('specifity_lin', types.Numeric, nullable=False),
    Column('specifity_cos', types.Numeric, nullable=False),
    Column('specifity_log', types.Numeric, nullable=False),
    Column('dataset_count', types.BigInteger, nullable=False),
    )
    
    
class VocabularySpecifity(domain_object.DomainObject):
    def __init__(self, vocabulary):
        self.vocabulary = vocabulary
    
    
meta.mapper(VocabularySpecifity, vocabulary_specifity_table)

