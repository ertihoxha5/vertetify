CREATE TABLE registry_profile (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    reference text UNIQUE
);
ALTER TABLE diplomas ADD registry_profile text REFERENCES registry_profile(reference);
