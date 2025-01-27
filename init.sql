CREATE TABLE allowed_users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE NOT NULL,
    added_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE imei_checks (
    id SERIAL PRIMARY KEY,
    imei VARCHAR(15) NOT NULL,
    check_status BOOLEAN NOT NULL,
    check_details JSONB,
    checked_at TIMESTAMP DEFAULT NOW()
);