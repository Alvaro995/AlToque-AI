from app.core.database import SessionLocal

from app.users.models import User
from app.profiles.models import ClinicalProfile
from app.habits.models import HabitEvent


db = SessionLocal()


patients = [

    {
        "name": "Ana Torres",
        "email": "ana.demo@altoque.com",
        "age": 35,
        "weight": 65,
        "height": 1.68,
        "glucose": 100,
        "hba1c": 5.7,
        "habits": [
            ("walking",60,"minutes"),
            ("sleep",8,"hours"),
            ("water",2.5,"liters")
        ]
    },


    {
        "name": "Carlos Perez",
        "email": "carlos.demo@altoque.com",
        "age":45,
        "weight":85,
        "height":1.70,
        "glucose":110,
        "hba1c":6.1,
        "habits":[
            ("walking",20,"minutes"),
            ("sleep",6,"hours"),
            ("water",1.5,"liters")
        ]
    },


    {
        "name":"Jose Ramirez",
        "email":"jose.demo@altoque.com",
        "age":58,
        "weight":98,
        "height":1.75,
        "glucose":125,
        "hba1c":6.4,
        "habits":[
            ("walking",5,"minutes"),
            ("sleep",5,"hours"),
            ("water",1,"liters")
        ]
    }

]


for patient in patients:


    user = User(

        name=patient["name"],
        email=patient["email"],
        age=patient["age"]

    )


    db.add(user)
    db.commit()
    db.refresh(user)



    profile = ClinicalProfile(

        user_id=user.id,
        weight=patient["weight"],
        height=patient["height"],
        glucose=patient["glucose"],
        hba1c=patient["hba1c"]

    )


    db.add(profile)



    for habit in patient["habits"]:

        event = HabitEvent(

            user_id=str(user.id),
            habit_type=habit[0],
            value=habit[1],
            unit=habit[2],
            source="DEMO"

        )

        db.add(event)



    db.commit()


    print(
        f"Paciente creado: {user.id} - {user.name}"
    )



db.close()