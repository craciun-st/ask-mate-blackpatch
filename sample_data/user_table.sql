ALTER TABLE if EXISTS ONLY public.users DROP CONSTRAINT if EXISTS pk_user_id CASCADE;
ALTER TABLE if EXISTS ONLY public.users DROP CONSTRAINT if EXISTS fk_user_id CASCADE;
-- creating users table
DROP TABLE IF EXISTS public.users;
CREATE TABLE users (
    id serial NOT NULL,
    username TEXT NOT NULL,
    password VARCHAR NOT NULL,
    date_of_registration TIMESTAMP WITHOUT TIME ZONE
);
-- -- altering existing tables
-- ALTER TABLE ONLY question
--     ADD user_id INTEGER;

-- ALTER TABLE ONLY answer
--     ADD user_id INTEGER;

-- ALTER TABLE ONLY comment
--     ADD user_id INTEGER;

--addin constraints for primary key in users table and foreign key in all the other tables that have 'user_id'
ALTER TABLE ONLY users
    ADD CONSTRAINT pk_user_id PRIMARY KEY (id);

ALTER TABLE ONLY comment 
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY question
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id);