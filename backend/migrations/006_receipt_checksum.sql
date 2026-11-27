ALTER TABLE diplomas
ADD registry_checksum varchar(64) NULL
	CHECK (registry_checksum IS NULL OR (LEN(registry_checksum) = 64 AND registry_checksum NOT LIKE '%[^0-9a-f]%'));
