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
    endpoints TEXT,
    user_id INTEGER,
    created TEXT,
    updated TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- migrate:down
DROP TABLE users;
DROP TABLE apis;
