-- Q2. How does revenue change month by month?
-- Skills: CTE, strftime, window functions LAG() and moving AVG()
-- Only complete months (2017-01 .. 2018-08) are used: the first and last months of the data are partial.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', o.order_purchase_timestamp) AS month,
        COUNT(DISTINCT o.order_id)                    AS orders,
        ROUND(SUM(oi.price), 2)                       AS revenue
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
)
SELECT
    month,
    orders,
    revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
                / LAG(revenue) OVER (ORDER BY month), 1)             AS mom_growth_pct,
    ROUND(AVG(revenue) OVER (ORDER BY month
                             ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS revenue_3m_avg
FROM monthly
WHERE month BETWEEN '2017-01' AND '2018-08'
ORDER BY month;
