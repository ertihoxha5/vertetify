ALTER TABLE diplomas ADD COLUMN registry_checksum text CHECK (registry_checksum ~ '^[0-9a-f]{64}$');
