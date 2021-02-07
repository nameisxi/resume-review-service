DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS resumes;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email TEXT,
    password TEXT,
    reviewer BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)

CREATE TABLE resumes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    reviewer_id INTEGER REFERENCES users,
    file_address TEXT,
    name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP    
)

INSERT INTO users (email,password,reviewer) VALUES ('henri@testi.fi', '123', false)
INSERT INTO users (email,password,reviewer) VALUES ('samu@testi.fi', '123', false)
INSERT INTO users (email,password,reviewer) VALUES ('tuomo@admin.fi', '123', true)

INSERT INTO resumes (user_id,reviewer_id,file_address,name) VALUES(1,3,'./resumes/test_resume.pdf','test_resume.pdf')
INSERT INTO resumes (user_id,reviewer_id,file_address,name) VALUES(2,3,'./resumes/test_resume.pdf','test_resume.pdf');