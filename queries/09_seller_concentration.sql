-- Q9. Is revenue concentrated in a few sellers? (Pareto analysis)
-- Skills: ROW_NUMBER, running total (cumulative SUM) with a window frame, COUNT(*) OVER ()
WITH seller_revenue AS (
    SELECT oi.seller_id, SUM(oi.price) AS revenue
    FROM order_items oi
    JOIN orders o ON o.order_id = oi.order_id AND o.order_status = 'delivered'
    GROUP BY oi.seller_id
),
ranked AS (
    SELECT
        seller_id,
        revenue,
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS seller_rank,
        COUNT(*)     OVER ()                      AS n_sellers,
        SUM(revenue) OVER (ORDER BY revenue DESC
                           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_revenue,
        SUM(revenue) OVER ()                      AS total_revenue
    FROM seller_revenue
)
SELECT
    seller_rank,
    seller_id,
    ROUND(revenue, 0)                              AS revenue,
    ROUND(100.0 * seller_rank / n_sellers, 1)      AS pct_of_sellers,
    ROUND(100.0 * cum_revenue / total_revenue, 1)  AS cumulative_revenue_pct
FROM ranked
ORDER BY seller_rank;
