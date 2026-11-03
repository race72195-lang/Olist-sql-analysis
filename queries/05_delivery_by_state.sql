-- Q5. Where is delivery slow or often late?
-- Skills: date arithmetic with julianday, conditional aggregation (CASE), HAVING
SELECT
    c.customer_state AS state,
    COUNT(*)         AS orders,
    ROUND(AVG(julianday(o.order_delivered_customer_date)
            - julianday(o.order_purchase_timestamp)), 1) AS avg_delivery_days,
    ROUND(100.0 * AVG(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                           THEN 1.0 ELSE 0 END), 1)      AS late_pct
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY state
HAVING COUNT(*) >= 100
ORDER BY avg_delivery_days DESC;
