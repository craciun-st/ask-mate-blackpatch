-- WITH user_qajoin AS (
--     WITH user_qjoin AS (
--         SELECT users.*, count(question.id) as "qcount" FROM users LEFT JOIN question 
--         ON (users.id = question.user_id)        
--     ) 
--     SELECT user_qjoin.*, count(answer.id) as "acount" FROM user_qjoin LEFT JOIN answer 
--     ON (user_qjoin.id = answer.user_id)    
-- )
-- SELECT user_qajoin.*, count(comment.id) as "ccount" FROM user_qajoin LEFT JOIN comment 
-- ON (user_qajoin.id = comment.user_id)
-- GROUP BY
-- (user_qajoin.acount, user_qajoin.qcount, user_qajoin.username);


SELECT username, u.id, count(a.id) as "acount", count(q.id) as "qcount", count(c.id) as "ccount"
FROM 
   users AS u
   FULL JOIN
   answer AS a
   ON u.id = a.user_id
   FULL JOIN
   question AS q
   ON u.id = q.user_id
   FULL JOIN
   comment AS c 
   ON u.id = c.user_id
GROUP BY
    (u.id, username);