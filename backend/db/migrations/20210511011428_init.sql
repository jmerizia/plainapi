-- migrate:up
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    is_admin BOOLEAN,
    hashed_password TEXT,
    joined TEXT
);

CREATE TABLE apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    user_id INTEGER,
    created TEXT,
    updated TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    method TEXT,
    api_id INTEGER,
    location INTEGER,
    created TEXT,
    updated TEXT,
    FOREIGN KEY(api_id) REFERENCES apis(id)
);

CREATE TABLE fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint_id INTEGER,
    location INTEGER,
    value TEXT,
    created TEXT,
    updated TEXT,
    FOREIGN KEY(endpoint_id) REFERENCES endpoints(id)
);


-- migrate:down
DROP TABLE users;
DROP TABLE apis;
DROP TABLE endpoints;
DROP TABLE fields;
