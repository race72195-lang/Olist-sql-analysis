-- Q3. Which product categories bring the most revenue?
-- Skills: multi-table JOIN + LEFT JOIN, COALESCE, RANK(), share of total and running total with window functions
WITH cat AS (
    SELECT
        COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
        COUNT(DISTINCT oi.order_id) AS orders,
        SUM(oi.price)               AS revenue
    FROM order_items oi
    JOIN orders   o ON o.order_id = oi.order_id AND o.order_status = 'delivered'
    JOIN products p ON p.product_id = oi.product_id
    LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name
    GROUP BY category
)
SELECT
    RANK() OVER (ORDER BY revenue DESC)             AS revenue_rank,
    category,
    orders,
    ROUND(revenue, 0)                               AS revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1) AS revenue_share_pct,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
                                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
                / SUM(revenue) OVER (), 1)          AS cumulative_share_pct
FROM cat
ORDER BY revenue DESC
LIMIT 15;
