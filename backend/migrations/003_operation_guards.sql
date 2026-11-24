ALTER TABLE diplomas ADD COLUMN verify_attempts integer NOT NULL DEFAULT 0;
ALTER TABLE diplomas ADD COLUMN next_check timestamptz NOT NULL DEFAULT now();
CREATE INDEX pending_diplomas ON diplomas(mode,next_check) WHERE state IN ('queued','registered');

CREATE FUNCTION guard_diploma_state() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.reference IS NOT NULL AND NEW.reference IS DISTINCT FROM OLD.reference THEN
        RAISE EXCEPTION 'receipt reference is immutable';
    END IF;
    IF NEW.state <> OLD.state AND NOT (
        (OLD.state='draft' AND NEW.state='queued') OR
        (OLD.state='queued' AND NEW.state='dispatching') OR
        (OLD.state='dispatching' AND NEW.state IN ('registered','review')) OR
        (OLD.state='registered' AND NEW.state IN ('issued','review')) OR
        (OLD.state='review' AND NEW.state='registered')
    ) THEN RAISE EXCEPTION 'invalid diploma transition';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_state BEFORE UPDATE ON diplomas FOR EACH ROW EXECUTE FUNCTION guard_diploma_state();

CREATE FUNCTION retain_diploma_event() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit events are append-only';
END $$;
CREATE TRIGGER guard_event BEFORE UPDATE OR DELETE ON diploma_events FOR EACH ROW EXECUTE FUNCTION retain_diploma_event();
