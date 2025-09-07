# knowledge_base_search

## Entities
- kb_articles
- tags
- article_tags
- article_views
- feedback

## Distinctiveness
Supports tagging and feedback for knowledge base articles.

## Indexes
- `article_views(article_id, viewed_at)`
- `feedback(article_id)`

## Expected Row Counts
- articles: 500
- views: 20k

## Efficiency Notes
Composite indexes ensure quick analytics on article engagement.
