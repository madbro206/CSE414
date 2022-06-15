CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patient (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments (
    ID int,
    Time date,
    Patient_name varchar(255) REFERENCES Patient(Username),
    Caregiver_name varchar(255) REFERENCES Caregivers(Username),
    Vaccine_name varchar(255) REFERENCES  Vaccines(Name),
    PRIMARY KEY (ID)
);