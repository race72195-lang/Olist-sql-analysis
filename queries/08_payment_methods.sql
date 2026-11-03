-- Q8. How do customers pay?
-- Skills: JOIN, GROUP BY, share of total with a window function
SELECT
    p.payment_type,
    COUNT(DISTINCT p.order_id)                                     AS orders,
    ROUND(SUM(p.payment_value), 0)                                 AS total_value,
    ROUND(AVG(p.payment_value), 2)                                 AS avg_payment,
    ROUND(AVG(p.payment_installments), 1)                          AS avg_installments,
    ROUND(100.0 * SUM(p.payment_value)
                / SUM(SUM(p.payment_value)) OVER (), 1)            AS value_share_pct
FROM payments p
JOIN orders o ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.payment_type
ORDER BY total_value DESC;
