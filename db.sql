DROP TABLE dataset_lodstats_partition_revision;
DROP TABLE dataset_lodstats_partition;
DROP TABLE dataset_lodstats_revision;
DROP TABLE dataset_lodstats;

CREATE TABLE dataset_lodstats
(
    id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    in_progress BOOLEAN NOT NULL,
    last_evaluated TIMESTAMP WITHOUT TIME ZONE,
    error TEXT,
    warning_count BIGINT,
    last_warning TEXT,
    rdf TEXT,
    triple_count BIGINT,
    class_count BIGINT,
    property_count BIGINT,
    vocabulary_count BIGINT,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE dataset_lodstats_revision
(
    id TEXT,
    dataset_id TEXT NOT NULL,
    in_progress BOOLEAN NOT NULL,
    last_evaluated TIMESTAMP WITHOUT TIME ZONE,
    error TEXT,
    warning_count BIGINT,
    last_warning TEXT,
    rdf TEXT,
    triple_count BIGINT,
    class_count BIGINT,
    property_count BIGINT,
    vocabulary_count BIGINT,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    
    continuity_id TEXT REFERENCES dataset_lodstats (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    expired_id TEXT,
    revision_timestamp TIMESTAMP WITHOUT TIME ZONE,
    expired_timestamp TIMESTAMP WITHOUT TIME ZONE,
    "current" BOOLEAN,
    
    CONSTRAINT dataset_lodstats_revision_pkey PRIMARY KEY (id, revision_id)
);

CREATE TABLE dataset_lodstats_partition
(
    id TEXT PRIMARY KEY ,
    dataset_lodstats_id TEXT NOT NULL REFERENCES dataset_lodstats (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    type TEXT NOT NULL,
    uir TEXT NOT NULL,
    uri_count BIGINT NOT NULL,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION
);

CREATE TABLE dataset_lodstats_partition_revision
(
    id TEXT,
    dataset_lodstats_id TEXT NOT NULL REFERENCES dataset_lodstats (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    type TEXT NOT NULL,
    uri TEXT NOT NULL,
    uri_count BIGINT NOT NULL,
    
    state TEXT,
    revision_id TEXT REFERENCES revision (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    
    continuity_id TEXT REFERENCES dataset_lodstats (id) ON UPDATE NO ACTION ON DELETE NO ACTION,
    expired_id TEXT,
    revision_timestamp TIMESTAMP WITHOUT TIME ZONE,
    expired_timestamp TIMESTAMP WITHOUT TIME ZONE,
    "current" BOOLEAN,
    
    CONSTRAINT dataset_lodstats_partition_revision_pkey PRIMARY KEY (id, revision_id)
);

