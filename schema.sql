-- Users table
CREATE TABLE  app.users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Hashed passwords (e.g., bcrypt in Python)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat history table
CREATE TABLE app.chat_history (
    chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app.users(user_id) ON DELETE CASCADE,
    message JSONB NOT NULL, -- JSONB for flexible message structure
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_message CHECK (message != '{}') -- Ensure message isn't empty
);


-- Database credentials table (stores encrypted credentials)
CREATE TABLE app.database_credentials (
    credential_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES app.users(user_id) ON DELETE CASCADE, -- Link to user
    service_name VARCHAR(100) NOT NULL, -- e.g., 'user_postgres_db'
    encrypted_credentials BYTEA NOT NULL, -- Encrypted credentials from Python
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_service UNIQUE (user_id, service_name) -- One service per user
);