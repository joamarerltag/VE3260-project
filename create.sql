CREATE TABLE Bruker(
	epostadresse TEXT PRIMARY KEY,
	passordhash TEXT NOT NULL,
	fornavn TEXT,
	etternavn TEXT
);

CREATE TABLE Sesjon(
	sesjonsID INTEGER PRIMARY KEY,
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
