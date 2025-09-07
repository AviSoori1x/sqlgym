-- views per article
SELECT article_id, COUNT(*) FROM article_views GROUP BY article_id;

-- helpfulness rate
SELECT article_id, AVG(helpful) FROM feedback GROUP BY article_id;

-- tag counts
SELECT tag_id, COUNT(*) FROM article_tags GROUP BY tag_id;
