-- Q1. How big is the business? (delivered orders only)
-- Skills: JOIN across 3 tables, aggregate functions, COUNT DISTINCT
SELECT
    COUNT(DISTINCT o.order_id)                              AS delivered_orders,
    COUNT(DISTINCT c.customer_unique_id)                    AS unique_customers,
    ROUND(SUM(oi.price), 0)                                 AS revenue,
    ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id), 2)    AS avg_order_value,
    ROUND(100.0 * SUM(oi.freight_value) / SUM(oi.price), 1) AS freight_pct_of_revenue,
    MIN(substr(o.order_purchase_timestamp, 1, 10))          AS first_order,
    MAX(substr(o.order_purchase_timestamp, 1, 10))          AS last_order
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN customers  c  ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered';
