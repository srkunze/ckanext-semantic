A CKAN Extension -- ckanext-semantic
====================================
Extraction of semantic data of RDF datasets of CKAN

**Features**

 - enhanced search (search after vocabularies, classes, properties, geographical and temporal coverage)
 - new search type: SPARQL
 - new subscription type: SPARQL subscriptions
 - enriched dataset page (used vocabularies, geographical and temporal coverage)
 - similar datasets
 - personalized recommendations

**Installation instructions**

 - install Virtuoso
 - install FedX in case of more endpoints
 - apply db.sql file to add necessary tables
 - install LODStats via pip (https://github.com/srkunze/LODStats)

<pre>
pip install -e git+https://github.com/srkunze/ckanext-semantic#egg=ckanext-semantic
pip install -e git+https://github.com/srkunze/LODStats#LODStats
</pre>

 - add to your CKAN configuration file

<pre>
# add this to your plugins
ckan.plugins = semantic

# constants for dataset statistics update
ckan.semantic.waiting_time = 1
ckan.semantic.ratio_old_new = 0.4

# credentials for sparql clients (for delete and insert)
# pattern: SPARQL_{attribute}_{role}; attribute in [username, password, hostname]; role in [root]
ckan.semantic.SPARQL_username_root = dba
ckan.semantic.SPARQL_password_root = dba
ckan.semantic.SPARQL_hostname_root = localhost

# federation tool fedX required
ckan.semantic.FedX = {path to your FedX}/lib/*

# endpoints
# pattern: SPARQL_endpoint# from 0 to 20
ckan.semantic.SPARQL_endpoint1 = http://localhost:8890/sparql
ckan.semantic.SPARQL_endpoint1_name = CKAN Store
ckan.semantic.SPARQL_endpoint2 = http://dbpedia.org/sparql
ckan.semantic.SPARQL_endpoint2_name = DBPedia Store
</pre>

 - create CRON jobs to run these commands on a periodical basis

<pre>
paster semantic update_dataset_due_statistics --config=../ckan/development.ini
paster semantic update_dataset_statistics {dataset_name} --config=../ckan/development.ini
paster semantic update_vocabulary_statistics --config=../ckan/development.ini
</pre>



Copyright and License
=====================
2013 © Sven R. Kunze

Licensed under the GNU Affero General Public License (AGPL) v3.0

http://www.fsf.org/licensing/licenses/agpl-3.0.html
