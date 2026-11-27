ALTER TABLE members DROP CONSTRAINT members_role_check;
ALTER TABLE members ADD CHECK (role IN ('registrar','holder','auditor','admin','superadmin','inactive'));
INSERT INTO tenants VALUES ('platform','Vertetify operations');
INSERT INTO members VALUES ('platform','fixture-operator','superadmin');

CREATE TABLE institution_requests (
    id uuid PRIMARY KEY, name text NOT NULL, contact text NOT NULL, mode text NOT NULL,
    tenant text REFERENCES tenants(id), submitted timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE access_invitations (
    digest bytea PRIMARY KEY, tenant text NOT NULL REFERENCES tenants(id), mode text NOT NULL,
    role text NOT NULL CHECK(role IN ('admin','registrar','auditor','holder')),
    expires timestamptz NOT NULL DEFAULT (now() + INTERVAL '48 hours'), used boolean NOT NULL DEFAULT false
);
CREATE TABLE invited_logins (
    tenant text NOT NULL, member text PRIMARY KEY, mode text NOT NULL, secret bytea NOT NULL,
    FOREIGN KEY(tenant,member) REFERENCES members(tenant_id,id)
);
CREATE TABLE access_events (
    sequence bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, occurred timestamptz NOT NULL DEFAULT now(),
    mode text NOT NULL, actor text NOT NULL, action text NOT NULL, subject text NOT NULL
);
CREATE TRIGGER retain_access_event BEFORE UPDATE OR DELETE ON access_events
    FOR EACH ROW EXECUTE FUNCTION retain_diploma_event();
CREATE TABLE verification_counts (
    day date NOT NULL, mode text NOT NULL, outcome text NOT NULL, total bigint NOT NULL,
    PRIMARY KEY(day,mode,outcome)
);
CREATE INDEX diploma_evidence_time ON diploma_events(diploma,occurred) WHERE event='evidence_matched';
