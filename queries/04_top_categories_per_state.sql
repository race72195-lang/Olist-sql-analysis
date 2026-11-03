-- Q4. What are the 3 best-selling categories in each of the 5 biggest states?
-- Skills: ROW_NUMBER() with PARTITION BY, several CTEs, window SUM per group
WITH state_cat AS (
    SELECT
        c.customer_state AS state,
        COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
        SUM(oi.price)    AS revenue
    FROM order_items oi
    JOIN orders    o ON o.order_id = oi.order_id AND o.order_status = 'delivered'
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN products  p ON p.product_id = oi.product_id
    LEFT JOIN category_translation t ON t.product_category_name = p.product_category_name
    GROUP BY state, category
),
ranked AS (
    SELECT
        state, category, revenue,
        ROW_NUMBER() OVER (PARTITION BY state ORDER BY revenue DESC) AS rn,
        SUM(revenue)  OVER (PARTITION BY state)                      AS state_revenue
    FROM state_cat
),
top_states AS (
    SELECT DISTINCT state, state_revenue
    FROM ranked
    ORDER BY state_revenue DESC
    LIMIT 5
)
SELECT
    r.state,
    r.rn                                              AS rank_in_state,
    r.category,
    ROUND(r.revenue, 0)                               AS revenue,
    ROUND(100.0 * r.revenue / r.state_revenue, 1)     AS share_of_state_pct
FROM ranked r
JOIN top_states s ON s.state = r.state
WHERE r.rn <= 3
ORDER BY s.state_revenue DESC, r.rn;
