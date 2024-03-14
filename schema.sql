/**CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);**/

INSERT OR IGNORE INTO user (username, password)
VALUES ('admin', 'admin');

INSERT OR IGNORE INTO user (username, password)
VALUES ('yohann', 'password');

INSERT OR IGNORE INTO user (username, password)
VALUES ('test', 'test');