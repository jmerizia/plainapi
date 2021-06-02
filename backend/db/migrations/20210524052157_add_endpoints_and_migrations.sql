-- migrate:up
CREATE TABLE endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    api_id INTEGER,
    method TEXT,
    url TEXT,
    value TEXT,
    sql_query TEXT,
    updated TEXT,
    created TEXT,
    FOREIGN KEY(api_id) REFERENCES apis(id)
);

CREATE TABLE migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    updated TEXT,
    created TEXT,
    FOREIGN KEY(api_id) REFERENCES apis(id)
);


-- migrate:down

