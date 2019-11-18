from models import User, users


class CargarUsuarios:
    users = []
    c1 = User(1, "Jose", "pesygamer888@gmail.com", "1234")

    users.append(c1)

    def get_user(email):
        for user in users:
            if user.email == email:
                return user
        return None