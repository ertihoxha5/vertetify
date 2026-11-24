CREATE TABLE diplomas (
    id uuid PRIMARY KEY,
    tenant text NOT NULL REFERENCES tenants(id),
    holder text NOT NULL,
    mode text NOT NULL CHECK (mode IN ('simulator','compellio-local')),
    snapshot jsonb NOT NULL,
    nonce bytea NOT NULL CHECK (octet_length(nonce)=32),
    state text NOT NULL DEFAULT 'draft' CHECK (state IN ('draft','queued','dispatching','registered','issued','review')),
    reference text,
    UNIQUE (tenant,id),
    FOREIGN KEY (tenant,holder) REFERENCES members(tenant_id,id),
    CHECK (state NOT IN ('issued','registered') OR reference IS NOT NULL)
);
CREATE FUNCTION immutable_diploma() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF (NEW.id,NEW.tenant,NEW.holder,NEW.mode,NEW.snapshot,NEW.nonce)
        IS DISTINCT FROM (OLD.id,OLD.tenant,OLD.holder,OLD.mode,OLD.snapshot,OLD.nonce) THEN
        RAISE EXCEPTION 'sealed diploma';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_diploma BEFORE UPDATE ON diplomas FOR EACH ROW EXECUTE FUNCTION immutable_diploma();
CREATE TABLE diploma_shares (
    digest bytea PRIMARY KEY, tenant text NOT NULL, diploma uuid NOT NULL,
    expires timestamptz NOT NULL DEFAULT now()+interval '7 days', disabled boolean NOT NULL DEFAULT false,
    FOREIGN KEY (tenant,diploma) REFERENCES diplomas(tenant,id)
);
CREATE TABLE demo_sessions (
    digest bytea PRIMARY KEY, tenant text NOT NULL, member text NOT NULL, role text NOT NULL,
    started timestamptz NOT NULL DEFAULT now(), touched timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant,member) REFERENCES members(tenant_id,id)
);
CREATE TABLE diploma_events (
    sequence bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    occurred timestamptz NOT NULL DEFAULT now(), tenant text NOT NULL, diploma uuid NOT NULL,
    event text NOT NULL, FOREIGN KEY (tenant,diploma) REFERENCES diplomas(tenant,id)
);
