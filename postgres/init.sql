CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(id),
    filename TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE edits (
    id SERIAL PRIMARY KEY,
    document_id INT REFERENCES documents(id),
    version INT,
    edited_content TEXT,
    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);