PRAGMA foreign_keys=ON;
CREATE TABLE kb_articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);
CREATE INDEX idx_article_title ON kb_articles(title);
CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE article_tags (
    article_id INTEGER NOT NULL REFERENCES kb_articles(id),
    tag_id INTEGER NOT NULL REFERENCES tags(id),
    PRIMARY KEY(article_id, tag_id)
);
CREATE INDEX idx_article_tags_tag ON article_tags(tag_id);
CREATE TABLE article_views (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES kb_articles(id),
    viewed_at TEXT NOT NULL
);
CREATE INDEX idx_views_article_date ON article_views(article_id, viewed_at);
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    article_id INTEGER NOT NULL REFERENCES kb_articles(id),
    helpful INTEGER NOT NULL CHECK(helpful IN (0,1))
);
CREATE INDEX idx_feedback_article ON feedback(article_id);
