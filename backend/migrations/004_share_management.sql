ALTER TABLE diploma_shares ADD COLUMN management_id uuid NOT NULL DEFAULT gen_random_uuid();
ALTER TABLE diploma_shares ADD UNIQUE (management_id);
