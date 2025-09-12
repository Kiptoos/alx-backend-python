DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age  INTEGER NOT NULL
);

INSERT INTO users (name, age) VALUES
  ('Amina', 22),
  ('Brian', 41),
  ('Chen', 35),
  ('Dayo', 55),
  ('Elsa', 27),
  ('Fatma', 43);
