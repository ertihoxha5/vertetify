CREATE TABLE tenants (
    id text PRIMARY KEY,
    name text NOT NULL
);
CREATE TABLE members (
    tenant_id text REFERENCES tenants(id),
    id text NOT NULL,
    role text NOT NULL CHECK (role IN ('registrar', 'holder', 'auditor')),
    PRIMARY KEY (tenant_id, id)
);
CREATE TABLE simulator_receipts (
    tenant_id text REFERENCES tenants(id),
    reference text NOT NULL,
    digest text NOT NULL CHECK (digest ~ '^[0-9a-f]{64}$'),
    PRIMARY KEY (tenant_id, reference),
    UNIQUE (tenant_id, digest)
);
