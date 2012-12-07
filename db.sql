DROP TABLE dataset_statistics_configuration;
DROP TABLE similarity_configuration;


CREATE TABLE dataset_statistics_configuration
(
    dataset_id TEXT PRIMARY KEY,
    created TIMESTAMP WITHOUT TIME ZONE
);


CREATE TABLE similarity_configuration
(
    entity_uri TEXT,
    similarity_method_uri TEXT,
    created TIMESTAMP WITHOUT TIME ZONE,
    request_count INTEGER,
    CONSTRAINT pkey_entity_uri_similarity_method_uri PRIMARY KEY(entity_uri, similarity_method_uri)
);

