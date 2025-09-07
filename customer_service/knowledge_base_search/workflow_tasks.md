# Workflow for knowledge_base_search

```sql
-- step: view_counts
CREATE TEMP TABLE vc AS SELECT article_id, COUNT(*) AS views FROM article_views GROUP BY article_id;

-- step: feedback_join
-- depends: view_counts
SELECT v.article_id, v.views, AVG(f.helpful) AS helpful_rate FROM vc v LEFT JOIN feedback f ON v.article_id=f.article_id GROUP BY v.article_id;
```
