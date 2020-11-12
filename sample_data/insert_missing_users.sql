INSERT INTO users (id, username, password, date_of_registration) 
    VALUES 
        (0, 'Admin', '$2b$12$1tySSXuNe4DfwtpwC4SZveyEj57b9p9N70oXHVYNzvWDQT2lH3Dee', '2017-01-01 00:00:00'),
        (1, 'Just_a_Random_Visitor', '$2b$12$xEG/13j8J5hmcREuMCUgkuzsIUpPoVrVdr4lVn7R5Dne3z1q2Iskm', '2017-01-10 12:37:28')
    ON CONFLICT (id) DO UPDATE
        SET (username, password, date_of_registration) = (EXCLUDED.username, EXCLUDED.password, EXCLUDED.date_of_registration);

UPDATE question SET user_id = 1 WHERE ((user_id IS NULL) AND (id % 2 = 0));
UPDATE question SET user_id = 0 WHERE ((user_id IS NULL) AND (id % 2 = 1));

UPDATE answer SET user_id = 0 WHERE ((user_id IS NULL) AND (id % 2 = 0));
UPDATE answer SET user_id = 1 WHERE ((user_id IS NULL) AND (id % 2 = 1));

UPDATE comment SET user_id = 0 WHERE ((user_id IS NULL) AND (id % 2 = 0));
UPDATE comment SET user_id = 1 WHERE ((user_id IS NULL) AND (id % 2 = 1));