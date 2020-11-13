WITH x AS (
    WITH user_qajoin AS (
        WITH user_qjoin AS (
            SELECT users.id, count(question.id) as "qcount" 
            FROM users LEFT JOIN question 
            ON (users.id = question.user_id)        
            GROUP BY users.id
        ) 
        SELECT user_qjoin.id, user_qjoin.qcount, count(answer.id) as "acount" 
        FROM user_qjoin LEFT JOIN answer 
        ON (user_qjoin.id = answer.user_id)    
        GROUP BY (user_qjoin.id, user_qjoin.qcount)
    )
    SELECT user_qajoin.id, user_qajoin.qcount, user_qajoin.acount, count(comment.id) as "ccount" 
    FROM user_qajoin LEFT JOIN comment 
    ON (user_qajoin.id = comment.user_id)
    GROUP BY
    (user_qajoin.acount, user_qajoin.qcount, user_qajoin.id)
)
SELECT u.id, u.username, u.date_of_registration, x.qcount, x.acount, x.ccount, u.reputation 
FROM
    users AS u INNER JOIN x 
ON
    (u.id = x.id)
ORDER BY 
    u.reputation DESC;
