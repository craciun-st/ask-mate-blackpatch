select username, COUNT(users.id) from question inner JOIN users
 ON question.user_id = users.id
 GROUP BY username



select username, COUNT(users.id) from comment inner JOIN users
 ON comment.user_id = users.id
 GROUP BY username



select username, COUNT(users.id) from answer inner JOIN users
 ON answer.user_id = users.id
 GROUP BY username



select username, COUNT(users.id) from question inner JOIN users
 ON question.user_id = users.id
 GROUP BY username



select * from users;
select * from question;
select * from answer;
select * from comment;