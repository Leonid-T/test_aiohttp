CREATE TABLE permissions (
	id SERIAL NOT NULL, 
	perm_name VARCHAR(10) NOT NULL, 
	PRIMARY KEY (id)
);
CREATE SEQUENCE some_id_seq START 2;
CREATE TABLE "user" (
	id INTEGER NOT NULL, 
	name VARCHAR(32), 
	surname VARCHAR(32), 
	login VARCHAR(128) NOT NULL, 
	password VARCHAR(256) NOT NULL, 
	date_of_birth DATE, 
	permissions INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (login), 
	FOREIGN KEY(permissions) REFERENCES permissions (id) ON DELETE SET NULL
);
INSERT INTO permissions (id, perm_name) VALUES (1, 'block');
INSERT INTO permissions (id, perm_name) VALUES (2, 'admin');
INSERT INTO permissions (id, perm_name) VALUES (3, 'read');
INSERT INTO "user" (id, name, surname, login, password, date_of_birth, permissions)
VALUES (1, 'admin', 'admin', 'admin', '$5$rounds=535000$ezbe6yziD03yEQT9$gdlb4LWW6y4LVHWusWmfgSE.Klil8DXYXxHiNPPd8SB', DATE'1970-01-01', 2);