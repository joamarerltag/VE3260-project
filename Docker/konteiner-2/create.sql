CREATE TABLE Bruker(
	epostadresse TEXT PRIMARY KEY,
	passordhash TEXT NOT NULL,
	fornavn TEXT,
	etternavn TEXT
);

CREATE TABLE Sesjon(
	sesjonsID TEXT PRIMARY KEY,
	epostadresse TEXT,
	FOREIGN KEY(epostadresse)
	REFERENCES Bruker(epostadresse)
);

CREATE TABLE Dikt(
	diktID INTEGER PRIMARY KEY AUTOINCREMENT,
	dikt TEXT,
	epostadresse TEXT,
	FOREIGN KEY(epostadresse)
	REFERENCES Bruker(epostadresse)
);

INSERT INTO Bruker
VALUES ("test@testus.gov","9c690591b6da6fd241f2773127ce967f","Hans","Gebroikenlaich");

INSERT INTO Dikt (dikt, epostadresse)
VALUES ("Dikt på svikt er lit", "test@testus.gov");
INSERT INTO Dikt (dikt, epostadresse)
VALUES ("You led me in your bed, but now I sleep alone, trapped with the forgotten, in my detritus home. I hope you're happy now, I hope it every day, in case you didn't figure it out yet, I'm the doll you threw away", "test@testus.gov");
INSERT INTO Dikt (dikt, epostadresse)
VALUES ("Fool me once, strike one, but fool me twice, strike three", "test@testus.gov");
INSERT INTO Dikt (dikt, epostadresse)
VALUES ("I love inside jokes, I hope to be a part of one someday", "test@testus.gov");
