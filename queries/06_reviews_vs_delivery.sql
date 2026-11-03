-- Q6. Do late deliveries lead to worse reviews?
-- Skills: CTEs, pre-aggregation to avoid duplicate rows (an order can have several reviews), CASE bucketing
WITH order_review AS (
    SELECT order_id, AVG(review_score) AS score
    FROM reviews
    GROUP BY order_id
),
delivery AS (
    SELECT
        order_id,
        julianday(order_delivered_customer_date)
          - julianday(order_estimated_delivery_date) AS days_vs_estimate
    FROM orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
)
SELECT
    CASE
        WHEN d.days_vs_estimate <= -7 THEN '1. 7+ days early'
        WHEN d.days_vs_estimate <=  0 THEN '2. on time (up to 7 days early)'
        WHEN d.days_vs_estimate <=  7 THEN '3. 1-7 days late'
        ELSE                               '4. more than 7 days late'
    END                                              AS delivery_bucket,
    COUNT(*)                                         AS orders,
    ROUND(AVG(r.score), 2)                           AS avg_review_score,
    ROUND(100.0 * AVG(CASE WHEN r.score <= 2 THEN 1.0 ELSE 0 END), 1) AS bad_review_pct
FROM delivery d
JOIN order_review r ON r.order_id = d.order_id
GROUP BY delivery_bucket
ORDER BY delivery_bucket;
