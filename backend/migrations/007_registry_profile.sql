CREATE TABLE registry_profile (
    singleton bit PRIMARY KEY DEFAULT (1) CHECK (singleton = 1),
    reference text UNIQUE
);
ALTER TABLE diplomas ADD registry_profile text REFERENCES registry_profile(reference);
