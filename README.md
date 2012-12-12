ckanext-lodstats
================

integration of lodstats and personalization features based on it

Installation instructions:

 - apply db file to add necessary tables
 - install LODStats via pip (https://github.com/srkunze/LODStats)
 - add to your CKAN configuration ini file

<pre>
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

 - run via paster
<pre>
paster semantic update_dataset_due_statistics --config=../ckan/development.ini
paster semantic update_dataset_statistics {dataset_name} --config=../ckan/development.ini
paster semantic update_vocabulary_statistics --config=../ckan/development.ini
</pre>
 - create CRON job to run these commands on a periodical basis
