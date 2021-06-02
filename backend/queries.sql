SELECT * FROM users WHERE id = ?;
SELECT * FROM users WHERE email = ?;
INSERT INTO users (email, hashed_password, is_admin, joined) VALUES (?, ?, ?, ?);
UPDATE users SET email = ?;
UPDATE users SET hashed_password = ?;
UPDATE users SET is_admin = ?;
UPDATE users SET joined = ?;
DELETE FROM users WHERE id = ?;

SELECT * FROM apis WHERE id = ?;
SELECT * FROM apis WHERE user_id = ?;
INSERT INTO apis (title, user_id, created, updated) VALUES (?, ?, ?, ?);
UPDATE apis SET title = ?;
UPDATE apis SET user_id = ?;
UPDATE apis SET created = ?;
UPDATE apis SET updated = ?;
DELETE FROM apis WHERE id = ?;

SELECT * FROM endpoints WHERE id = ?;
SELECT * FROM endpoints WHERE api_id = ?;
INSERT INTO endpoints (api_id, method, url, value, sql_query) VALUES (?, ?, ?, ?, ?);
UPDATE apis SET api_id = ?;
UPDATE apis SET method = ?;
UPDATE apis SET url = ?;
UPDATE apis SET value = ?;
UPDATE apis SET sql_query = ?;
DELETE FROM apis WHERE id = ?;

SELECT * FROM migrations WHERE id = ?;
SELECT * FROM migrations WHERE api_id = ?;
INSERT INTO migrations (api_id, value, applied, sql_query) VALUES (?, ?, ?, ?);
UPDATE migrations SET api_id = ?;
UPDATE migrations SET value = ?;
UPDATE migrations SET applied = ?;
UPDATE migrations SET sql_query = ?;
DELETE FROM apis WHERE id = ?;
