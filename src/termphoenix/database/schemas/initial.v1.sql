-- TermPhoenix Database Schema initial.v1
-- Single-project database with graph relationships

CREATE TABLE project_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE websites (
    website_id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    base_url TEXT,
    robots_txt TEXT,
    robots_last_fetched DATETIME,
    first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crawl_sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_url TEXT NOT NULL,
    parameters_json TEXT NOT NULL,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    status TEXT DEFAULT 'pending',
    total_pages INTEGER DEFAULT 0,
    allow_leave_domain BOOLEAN DEFAULT 0
);

CREATE TABLE pages (
    page_id INTEGER PRIMARY KEY AUTOINCREMENT,
    website_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    url_hash TEXT UNIQUE NOT NULL,
    raw_html BLOB,
    http_status INTEGER,
    content_type TEXT,
    last_crawled DATETIME DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    response_time_ms INTEGER,
    FOREIGN KEY (website_id) REFERENCES websites(website_id)
);

CREATE TABLE page_distances (
    distance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    page_id INTEGER NOT NULL,
    depth INTEGER NOT NULL,
    counter INTEGER DEFAULT 1,
    first_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES crawl_sessions(session_id),
    FOREIGN KEY (page_id) REFERENCES pages(page_id),
    UNIQUE(session_id, page_id, depth)
);

CREATE TABLE page_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    referer_page_id INTEGER NOT NULL,
    target_page_id INTEGER,
    target_url TEXT NOT NULL,
    target_url_hash TEXT NOT NULL,
    link_counter INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES crawl_sessions(session_id),
    FOREIGN KEY (referer_page_id) REFERENCES pages(page_id),
    FOREIGN KEY (target_page_id) REFERENCES pages(page_id),
    UNIQUE(session_id, referer_page_id, target_url_hash)
);

-- Performance indexes
CREATE INDEX idx_pages_url_hash ON pages(url_hash);
CREATE INDEX idx_pages_website ON pages(website_id);
CREATE INDEX idx_pages_last_crawled ON pages(last_crawled);
CREATE INDEX idx_distances_session_page ON page_distances(session_id, page_id);
CREATE INDEX idx_distances_depth ON page_distances(depth);
CREATE INDEX idx_links_referer ON page_links(referer_page_id);
CREATE INDEX idx_links_target ON page_links(target_url_hash);
CREATE INDEX idx_links_session ON page_links(session_id);
CREATE INDEX idx_websites_domain ON websites(domain);
CREATE INDEX idx_sessions_status ON crawl_sessions(status);

-- Insert initial metadata
-- This is removed because we do this in the setup method itself. And we want to strictly separate data from schema.
--INSERT INTO project_metadata (key, value) VALUES 
--    ('schema_version', '1.0'),
--    ('created_at', datetime('now'));
