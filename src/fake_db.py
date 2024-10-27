# Base de données des utilisateurs (simulée)
fake_users_db = {
    "JerMac": {
        "username": "JerMac",
        "full_name": "Jeremy Maceiras",
        "email": "jeremy.maceira@edu.vs.ch",
        "hashed_password": "fakehashedpwd4m321prof",
        "disabled": False,
        "role": "enseignant",
    },
    "TanArg": {
        "username": "TanArg",
        "full_name": "Tancrède Arguillère",
        "email": "tancrede.arguillere@edu.vs.ch",
        "hashed_password": "fakehashedpwd4m321prof",
        "disabled": False,
        "role": "enseignant",
    },
    "JessFerr": {
        "username": "JessFerr",
        "full_name": "Jessica Ferreira",
        "email": "jessica.ferreira5@edu.vs.ch",
        "hashed_password": "fakehashedpwd4m321student",
        "disabled": False,
        "role": "eleve",
    },
    "YannBerl": {
        "username": "YannBerl",
        "full_name": "Yann Berlemond",
        "email": "yann.berlemond@edu.vs.ch",
        "hashed_password": "fakehashedpwd4m321student",
        "disabled": False,
        "role": "eleve",
    },
    "AndrSoar": {
        "username": "AndrSoar",
        "full_name": "André Soares",
        "email": "andre.soares@edu.vs.ch",
        "hashed_password": "fakehashedpwd4m321student",
        "disabled": False,
        "role": "eleve",
    }
}

# Base de données des classes 
fake_classes_db = {
    "M321": {
        "teacher": "JerMac",  # L'enseignant responsable de la classe M321
        "students": ["JessFerr", "AndrSoar"]  # Les élèves inscrits dans la classe M321
    },
    "CG": {
        "teacher": "TanArg",  # L'enseignant responsable de la classe CG
        "students": ["YannBerl"]  # Les élèves inscrits dans la classe CG
    }
}
