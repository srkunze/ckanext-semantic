DROP TABLE dataset_lodstats_class_partition_revision;
DROP TABLE dataset_lodstats_class_partition;
DROP TABLE dataset_lodstats_revision;
DROP TABLE dataset_lodstats;

CREATE TABLE dataset_lodstats
(
    dataset_id TEXT PRIMARY KEY,
    in_progress BOOLEAN NOT NULL,
    last_evaluated TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    error TEXT,
    warnings BIGINT,
    last_warning TEXT,
    RDF TEXT,
    triples BIGINT,
    classes BIGINT,
    properties BIGINT,
    vocabularies BIGINT,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE dataset_lodstats_revision
(
    dataset_id TEXT NOT NULL,
    in_progress BOOLEAN NOT NULL,
    last_evaluated TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    error TEXT,
    warning_count BIGINT NOT NULL,
    last_warning TEXT,
    rdf TEXT NOT NULL,
    triple_count BIGINT NOT NULL,
    class_count BIGINT NOT NULL,
    property_count BIGINT NOT NULL,
    vocabulary_count BIGINT NOT NULL,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    
    continuity_id TEXT REFERENCES dataset_lodstats (dataset_id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    expired_id TEXT,
    revision_timestamp TIMESTAMP WITHOUT TIME ZONE,
    expired_timestamp TIMESTAMP WITHOUT TIME ZONE,
    "current" BOOLEAN,
    
    CONSTRAINT dataset_lodstats_revision_pkey PRIMARY KEY (dataset_id, revision_id)
);

CREATE TABLE dataset_lodstats_class_partition
(
    dataset_id TEXT PRIMARY KEY REFERENCES dataset_lodstats (dataset_id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    type TEXT NOT NULL,
    uir TEXT NOT NULL,
    uri_count BIGINT NOT NULL,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE dataset_lodstats_class_partition_revision
(
    dataset_id TEXT REFERENCES dataset_lodstats (dataset_id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    type TEXT NOT NULL,
    uri TEXT NOT NULL,
    uri_count BIGINT NOT NULL,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    
    continuity_id TEXT REFERENCES dataset_lodstats (dataset_id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    expired_id TEXT,
    revision_timestamp TIMESTAMP WITHOUT TIME ZONE,
    expired_timestamp TIMESTAMP WITHOUT TIME ZONE,
    "current" BOOLEAN,
    
    CONSTRAINT dataset_lodstats_class_partition_revision_pkey PRIMARY KEY (dataset_id, revision_id)
);

