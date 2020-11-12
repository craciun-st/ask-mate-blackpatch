ALTER TABLE ONLY users ADD reputation INTEGER;
UPDATE users SET reputation = 0 WHERE reputation IS NULL;