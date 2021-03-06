CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT,
    password TEXT,
    reviewer BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    reviewer_id INTEGER REFERENCES users,
    file_address TEXT,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE  
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users,
    resume_id INTEGER REFERENCES resumes,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES users,
    resume_id INTEGER REFERENCES resumes,
    rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);
