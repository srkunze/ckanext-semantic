DROP TABLE dataset_stats;

CREATE TABLE dataset_stats
(
    dataset_id TEXT PRIMARY KEY,
    last_evaluated TIMESTAMP WITHOUT TIME ZONE
);
