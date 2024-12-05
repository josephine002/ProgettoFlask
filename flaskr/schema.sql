DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

DROP TABLE IF EXISTS "Exercise";
DROP TABLE IF EXISTS "Fisioterapista";
DROP TABLE IF EXISTS "Paziente";
DROP TABLE IF EXISTS "Programma";
DROP TABLE IF EXISTS "PatientExercises";

CREATE TABLE Exercise (
    ID_exercise INTEGER PRIMARY KEY AUTOINCREMENT,
    URL TEXT NOT NULL,
    package_id INTEGER NOT NULL,
    FOREIGN KEY (package_id) REFERENCES ExercisePackage (ID_package)
);

CREATE TABLE PatientExercises (
    ID_patient INTEGER NOT NULL,
    ID_package INTEGER NOT NULL,
    PRIMARY KEY (ID_patient, ID_package),
    FOREIGN KEY (ID_patient) REFERENCES Paziente (ID_paziente),
    FOREIGN KEY (ID_package) REFERENCES ExercisePackage (ID_package)
);

CREATE TABLE "Fisioterapista" (
  "ID_Fisio" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ID_utente" INTEGER,
  "specializzazione" TEXT,
  "posizione_clinica" TEXT,
  CONSTRAINT "utente" FOREIGN KEY("ID_utente") REFERENCES "Utente"("ID_utente")
);

CREATE TABLE Paziente (
    ID_paziente INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_utente INTEGER NOT NULL,
    Data_di_nascita TEXT NOT NULL,
    genere TEXT NOT NULL,
    motivo_visita TEXT NOT NULL,
    ID_FIsio INTEGER NOT NULL,
    FOREIGN KEY (ID_utente) REFERENCES user (id),
    FOREIGN KEY (ID_FIsio) REFERENCES user (id)
);

CREATE TABLE "Programma" (
  "ID_prog" INTEGER PRIMARY KEY AUTOINCREMENT,
  "ID_paziente" INTEGER,
  "ID_fisio" INTEGER,
  "Data_inizio" TEXT,
  "Data_fine" TEXT,
  FOREIGN KEY("ID_fisio") REFERENCES "Fisioterapista"("ID_Fisio"),
  FOREIGN KEY("ID_paziente") REFERENCES "Paziente"("ID_paziente")
);

CREATE TABLE IF NOT EXISTS "Programma Esercizi" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    descrizione TEXT,
    data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

