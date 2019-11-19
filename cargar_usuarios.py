from models import User, users
import cx_Oracle

connection = cx_Oracle.connect("fbd/fbd@localhost:49161/xe")


class CargarUsuarios:

    def get_user(email):
        users = []
        connection = cx_Oracle.connect("fbd/fbd@localhost:49161/xe")
        cur = connection.cursor()
        cur.execute("SELECT * FROM USUARIOS WHERE correo=:1", (email,))
        col = cur.fetchall()
        for c in col:
            id = c[0]
            name = c[1]
            lastN = c[2]
            email = c[3]
            password = c[4]
            admin = True if c[5] == "1" else False
            users.append(User(id, name, lastN, email, password, is_admin=admin))

        cur.close()
        connection.close()

        for user in users:
            print(user)
            if user.email == email:
                return user
        return None


if __name__ == "__main__":
    a = CargarUsuarios()
