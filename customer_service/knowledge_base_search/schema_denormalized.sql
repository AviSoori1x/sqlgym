PRAGMA foreign_keys=OFF;
CREATE TABLE article_usage AS
SELECT a.id AS article_id, a.title, v.viewed_at, f.helpful
FROM kb_articles a
LEFT JOIN article_views v ON a.id=v.article_id
LEFT JOIN feedback f ON a.id=f.article_id;
