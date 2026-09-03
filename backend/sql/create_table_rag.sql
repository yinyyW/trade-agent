

CREATE TABLE knowledge_document (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    source_type VARCHAR(30) NOT NULL,
    source_url VARCHAR(1000) NULL,
    author VARCHAR(100) NULL,
    version VARCHAR(50) NOT NULL,
    content LONGTEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    INDEX idx_knowledge_document_category (category),
    INDEX idx_knowledge_document_status (status)
);

CREATE TABLE knowledge_chunk (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    document_id BIGINT NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT NOT NULL,
    content_hash CHAR(64) NOT NULL,
    vector_id VARCHAR(100) NULL,
    metadata JSON NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    CONSTRAINT fk_knowledge_chunk_document
        FOREIGN KEY (document_id)
        REFERENCES knowledge_document(id),
    INDEX idx_knowledge_chunk_document_id (document_id),
    INDEX idx_knowledge_chunk_content_hash (content_hash),
    UNIQUE KEY uk_knowledge_chunk_position (document_id, chunk_index)
);