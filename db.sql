DROP TABLE dataset_stats;
DROP TABLE similarity_configuration;


CREATE TABLE dataset_stats
(
    dataset_uri TEXT PRIMARY KEY,
    created TIMESTAMP WITHOUT TIME ZONE
);


CREATE TABLE similarity_configuration
(
    entity_uri TEXT,
    similarity_method_uri TEXT,
    request_count INTEGER,
    created TIMESTAMP WITHOUT TIME ZONE,
    CONSTRAINT pkey_entity_uri_similarity_method_uri PRIMARY KEY(entity_uri, similarity_method_uri)
);

