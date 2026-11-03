-- Q7. How many customers come back?
-- Skills: aggregation over aggregation, window function over GROUP BY result
-- Note: customer_id is new for every order, so repeat buyers are identified by customer_unique_id.
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.price)              AS revenue
    FROM orders o
    JOIN customers   c  ON c.customer_id = o.customer_id
    JOIN order_items oi ON oi.order_id   = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)
SELECT
    CASE WHEN orders = 1 THEN '1 order'
         WHEN orders = 2 THEN '2 orders'
         ELSE '3+ orders' END                                         AS segment,
    COUNT(*)                                                          AS customers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)                AS customers_pct,
    ROUND(SUM(revenue), 0)                                            AS revenue,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1)        AS revenue_pct
FROM customer_orders
GROUP BY segment
ORDER BY segment;
