CREATE TABLE IF NOT EXISTS "schema_migrations" (version varchar(255) primary key);
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    is_admin BOOLEAN,
    hashed_password TEXT,
    joined TEXT
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE apis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    endpoints TEXT,
    user_id INTEGER,
    created TEXT,
    updated TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
-- Dbmate schema migrations
INSERT INTO "schema_migrations" (version) VALUES
  ('20210511011428');
