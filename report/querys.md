<!-- Query 1 – Total Subscribers (Fixed Card) -->

SELECT
    COUNT(*) AS total_subscribers
FROM customer_features;

<!-- Query 2 – Churn Rate (Selected Filters) -->

SELECT
    ab_group,
    COUNT(*) AS total_subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
GROUP BY ab_group
ORDER BY ab_group;


<!-- Query 3 – Current Filter Churn Rate -->

SELECT
    COUNT(*) AS total_subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE
    (:connection_type = 'All'
     OR connection_type = :connection_type)
    AND
    (:region = 'All'
     OR region = :region);

<!-- Query 4 – Churn by Complete Years on Network -->

SELECT
    tenure_years,
    COUNT(*) AS subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE
    (:connection_type = 'All'
     OR connection_type = :connection_type)
    AND
    (:region = 'All'
     OR region = :region)
GROUP BY tenure_years
ORDER BY tenure_years;


<!-- Query 5 – Prepaid vs Postpaid Churn -->

SELECT
    connection_type,
    COUNT(*) AS subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE
    (:connection_type = 'All'
     OR connection_type = :connection_type)
    AND
    (:region = 'All'
     OR region = :region)
GROUP BY connection_type
ORDER BY churn_rate DESC;


<!-- Query 6 – Churn Across All Circles -->

SELECT
    circle_name,
    region,
    COUNT(*) AS subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE
    (:connection_type = 'All'
     OR connection_type = :connection_type)
    AND
    (:region = 'All'
     OR region = :region)
GROUP BY circle_name, region
ORDER BY churn_rate DESC;


<!-- Query 7 – Circle Dropdown (Highest Churn First) -->

SELECT
    circle_name,
    region,
    COUNT(*) AS subscribers,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE
    (:connection_type = 'All'
     OR connection_type = :connection_type)
    AND
    (:region = 'All'
     OR region = :region)
GROUP BY circle_name, region
ORDER BY churn_rate DESC;

<!-- Query 8 – Selected Circle Subscribers and Churn -->

SELECT
    circle_name,
    COUNT(*) AS total_subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE circle_name = :selected_circle
    AND (:connection_type = 'All'
         OR connection_type = :connection_type)
    AND (:region = 'All'
         OR region = :region)
GROUP BY circle_name;

<!-- Query 9 – Selected Circle Tenure Churn -->

SELECT
    tenure_years,
    COUNT(*) AS subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE circle_name = :selected_circle
    AND (:connection_type = 'All'
         OR connection_type = :connection_type)
    AND (:region = 'All'
         OR region = :region)
GROUP BY tenure_years
ORDER BY tenure_years;

<!-- Query 10 – Selected Circle Prepaid vs Postpaid -->

SELECT
    connection_type,
    COUNT(*) AS subscribers,
    SUM(is_churned) AS subscribers_left,
    ROUND(100.0 * AVG(is_churned), 2) AS churn_rate
FROM customer_features
WHERE circle_name = :selected_circle
    AND (:connection_type = 'All'
         OR connection_type = :connection_type)
    AND (:region = 'All'
         OR region = :region)
GROUP BY connection_type
ORDER BY churn_rate DESC;

<!-- Query 11 – Selected Circle Open Complaint Tickets -->

SELECT
    COUNT(*) AS total_subscribers,
    SUM(
        CASE WHEN unresolved_count > 0
        THEN 1 ELSE 0 END
    ) AS open_ticket_subscribers,
    ROUND(
        100.0 * SUM(
            CASE WHEN unresolved_count > 0
            THEN 1 ELSE 0 END
        ) / COUNT(*), 2
    ) AS open_ticket_percentage
FROM customer_features
WHERE circle_name = :selected_circle
    AND (:connection_type = 'All'
         OR connection_type = :connection_type)
    AND (:region = 'All'
         OR region = :region);

