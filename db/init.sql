CREATE DATABASE immi;
use immi;

CREATE TABLE invitation (
  
  date date,
  category VARCHAR(100),
  amount VARCHAR(10)
);

INSERT INTO invitation
  (date, category, amount)
VALUES
  ('2022-02-25', 'CEC', '2500'),
  ('2022-01-01', 'FSW', '3500'),
  ('2021-12-01', 'PNP', '100');