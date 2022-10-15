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
	diktID INTEGER PRIMARY KEY,
	dikt TEXT,
	epostadresse TEXT,
	FOREIGN KEY(epostadresse)
	REFERENCES Bruker(epostadresse)
);

INSERT INTO Bruker
VALUES ("test@testus.gov","9c690591b6da6fd241f2773127ce967f","Hans","Gebroikenlaich");

INSERT INTO Dikt
VALUES (1, "Dikt på svikt", "test@testus.gov");
