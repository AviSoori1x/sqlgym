-- Sanity checks for digital ads attribution domain

-- 1. All ad groups reference valid campaigns
SELECT COUNT(*) FROM ad_groups ag LEFT JOIN campaigns c ON ag.campaign_id = c.id WHERE c.id IS NULL;

-- 2. All ads reference valid ad groups
SELECT COUNT(*) FROM ads a LEFT JOIN ad_groups ag ON a.ad_group_id = ag.id WHERE ag.id IS NULL;

-- 3. All touchpoints with campaign_id reference valid campaigns
SELECT COUNT(*) FROM touchpoints t LEFT JOIN campaigns c ON t.campaign_id = c.id WHERE t.campaign_id IS NOT NULL AND c.id IS NULL;

-- 4. All touchpoints with ad_group_id reference valid ad groups
SELECT COUNT(*) FROM touchpoints t LEFT JOIN ad_groups ag ON t.ad_group_id = ag.id WHERE t.ad_group_id IS NOT NULL AND ag.id IS NULL;

-- 5. All touchpoints with ad_id reference valid ads
SELECT COUNT(*) FROM touchpoints t LEFT JOIN ads a ON t.ad_id = a.id WHERE t.ad_id IS NOT NULL AND a.id IS NULL;

-- 6. Campaign platform enum validation
SELECT COUNT(*) FROM campaigns WHERE platform NOT IN ('GOOGLE_ADS', 'FACEBOOK', 'INSTAGRAM', 'TWITTER', 'TIKTOK', 'LINKEDIN', 'AMAZON');

-- 7. Campaign type enum validation
SELECT COUNT(*) FROM campaigns WHERE campaign_type NOT IN ('SEARCH', 'DISPLAY', 'VIDEO', 'SHOPPING', 'SOCIAL', 'RETARGETING');

-- 8. Campaign objective enum validation
SELECT COUNT(*) FROM campaigns WHERE objective NOT IN ('AWARENESS', 'TRAFFIC', 'ENGAGEMENT', 'LEADS', 'SALES', 'RETENTION');

-- 9. Campaign status enum validation
SELECT COUNT(*) FROM campaigns WHERE status NOT IN ('DRAFT', 'ACTIVE', 'PAUSED', 'COMPLETED', 'CANCELLED');

-- 10. Ad group bid strategy enum validation
SELECT COUNT(*) FROM ad_groups WHERE bid_strategy NOT IN ('CPC', 'CPM', 'CPA', 'ROAS', 'MAXIMIZE_CLICKS');

-- 11. Ad group status enum validation
SELECT COUNT(*) FROM ad_groups WHERE status NOT IN ('ACTIVE', 'PAUSED', 'REMOVED');

-- 12. Ad type enum validation
SELECT COUNT(*) FROM ads WHERE ad_type NOT IN ('TEXT', 'IMAGE', 'VIDEO', 'CAROUSEL', 'COLLECTION', 'DYNAMIC');

-- 13. Call to action enum validation
SELECT COUNT(*) FROM ads WHERE call_to_action IS NOT NULL AND call_to_action NOT IN ('LEARN_MORE', 'SHOP_NOW', 'SIGN_UP', 'DOWNLOAD', 'CONTACT_US');

-- 14. Ad status enum validation
SELECT COUNT(*) FROM ads WHERE status NOT IN ('ACTIVE', 'PAUSED', 'DISAPPROVED', 'REMOVED');

-- 15. Touchpoint platform enum validation
SELECT COUNT(*) FROM touchpoints WHERE platform NOT IN ('GOOGLE_ADS', 'FACEBOOK', 'INSTAGRAM', 'TWITTER', 'TIKTOK', 'LINKEDIN', 'AMAZON', 'ORGANIC');

-- 16. Touchpoint interaction type enum validation
SELECT COUNT(*) FROM touchpoints WHERE interaction_type NOT IN ('IMPRESSION', 'CLICK', 'VIEW', 'ENGAGEMENT', 'CONVERSION');

-- 17. Conversion type enum validation
SELECT COUNT(*) FROM conversions WHERE conversion_type NOT IN ('PURCHASE', 'SIGNUP', 'LEAD', 'DOWNLOAD', 'SUBSCRIBE', 'ADD_TO_CART');

-- 18. Attribution model type enum validation
SELECT COUNT(*) FROM attribution_models WHERE model_type NOT IN ('FIRST_TOUCH', 'LAST_TOUCH', 'LINEAR', 'TIME_DECAY', 'POSITION_BASED', 'DATA_DRIVEN');

-- 19. Campaign end date should be after start date
SELECT COUNT(*) FROM campaigns WHERE end_date IS NOT NULL AND end_date <= start_date;

-- 20. Targeting criteria should be valid JSON where present
SELECT COUNT(*) FROM ad_groups WHERE targeting_criteria IS NOT NULL AND json_valid(targeting_criteria) = 0;

-- 21. Attribution model parameters should be valid JSON where present
SELECT COUNT(*) FROM attribution_models WHERE parameters IS NOT NULL AND json_valid(parameters) = 0;

-- 22. Touchpoint timestamp should be valid datetime
SELECT COUNT(*) FROM touchpoints WHERE datetime(timestamp) IS NULL;

-- 23. Conversion timestamp should be valid datetime
SELECT COUNT(*) FROM conversions WHERE datetime(conversion_timestamp) IS NULL;

-- 24. EXPLAIN - Verify index usage for campaign platform queries
EXPLAIN QUERY PLAN SELECT * FROM campaigns WHERE platform = 'GOOGLE_ADS';

-- 25. EXPLAIN - Verify index usage for touchpoint timestamp range queries
EXPLAIN QUERY PLAN SELECT * FROM touchpoints WHERE timestamp >= '2024-01-01' AND timestamp < '2024-02-01';