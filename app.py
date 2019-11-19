import base64
from decimal import Decimal

from flask import Flask, url_for, redirect, request, render_template
from flask_login import LoginManager, current_user, login_user, logout_user
from werkzeug.urls import url_parse

import forms
from cargar_usuarios import CargarUsuarios
from forms import LoginForm
from models import users, get_user
import cx_Oracle

app = Flask(__name__)
app.config['SECRET_KEY'] = "7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe"
# ORACLE CONNECTION SET VARIABLES
connection = cx_Oracle.connect("fbd/fbd@localhost:49161/xe")

# IMAGE FOLDER STATEMENT
app.config['UPLOAD_FOLDER'] = './uploads'
login_manager = LoginManager(app)


def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return bytes(binaryData)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/login_test')
def login_test():
    return render_template("login_test.html")


@app.route('/albums', methods=["GET", "POST"])
def albums():
    form = forms.FormAlbum()
    if form.validate_on_submit():
        if request.method == "POST":
            idA = request.form["artista"]
            cur = connection.cursor()
            filename = forms.photos.save(form.portada.data)  # saves image
            im = convertToBinaryData("uploads/%s" % (filename))
            precio = Decimal(form.precio.data)
            p = "%.2f" % (precio)
            cur.execute("Insert into ALBUMS(ID_ARTISTA, NOMBRE, PORTADA, PRECIO, DIRECCION) values (:1,:2,:3,:4,:5)",
                        (idA, form.title.data, im, p, '-'))
            connection.commit()
            cur.close
        return "OK"
    cur = connection.cursor()
    cur.execute("SELECT * FROM ARTISTAS")
    data = cur.fetchall()
    if len(data) == 0:
        return "No puede añadir albumes si no hay artistas"
    cur.close()
    return render_template("AddAlbum.html", art_data=data, base64=base64, form=form)


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = CargarUsuarios.get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = '/'
            return redirect(next_page)
    return render_template('login_test.html', form=form)


@app.route("/agregar_usuarios")
def addUsers():
    return render_template("AgregarUsuarios.html")


@app.route("/add_user", methods=["POST"])
def agregar_usuario():
    if request.method == "POST":
        cur = connection.cursor()
        nombre = request.form["name"]
        apellidos = request.form["lastName"]
        email = request.form["email"]
        psswd = request.form["password"]
        try:
            cur.execute(
                "INSERT INTO usuarios(NOMBRE, APELLIDO, CORREO, PASSWORD, ES_ACTIVO) VALUES ('%s','%s','%s','%s','%s')" % (
                    nombre, apellidos, email, psswd, '0'))
            connection.commit()
            cur.close()
        except:
            return "El usuario ya existe"
            cur.close()

    return redirect("/agregar_usuarios")


if __name__ == '__main__':
    app.run()
