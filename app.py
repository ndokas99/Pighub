from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from sqlite3 import connect, OperationalError
from os import path

settings = {
    "SECRET_KEY": 'G15FH6HHD75DGFJ7JD9HD',
    "SQLALCHEMY_DATABASE_URI": 'sqlite:///accHolders.db',
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "lereck.sibanda@students.uz.ac.zw",
    "MAIL_PASSWORD": "R192093X"
}

app = Flask(__name__)
app.debug = False
mail = Mail(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/breeds')
def breedsPage():
    db = connect("database.db")
    records = db.execute("select * from breeds;").fetchall()
    breeds = []
    j = -1
    for i in range(len(records)):
        if i % 4 == 0:
            breeds.append([])
            j += 1
        breeds[j].append(records[i])
    return render_template("breeds.html", breeds=breeds)


@app.route('/breeding')
def breedingPage():
    return render_template("breeding.html")


@app.route('/diseaseAndParasites')
def disAndParaPage():
    return render_template("diseaseAndParasites.html")


@app.route('/housing')
def housingPage():
    return render_template("housing.html")


@app.route('/management')
def managementPage():
    return render_template("management.html")


@app.route('/shops')
def shopPage():
    db = connect("retailers.db")
    try:
        records = db.execute("select * from companies;").fetchall()
    except OperationalError:
        return
    collection = []
    j = -1
    for i in range(len(records)):
        if i % 3 == 0:
            collection.append([])
            j += 1
        collection[j].append(records[i])
    return render_template("shops.html", collection=collection)


@app.route('/join')
def joinPage():
    return render_template("join.html")


@app.route('/write', methods=['POST', 'GET'])
def write():
    if request.method == "POST":
        details = {
            'name': request.form['name'],
            'addr': request.form['address'],
            'cont': request.form['contacts'],
            'prod': request.form['products'],
            'serv': request.form['services'],
        }
        logo = request.files['logo']

        image = path.join(
            'static/images',
            secure_filename(f"{details['name']}.{logo.filename.split('.')[-1]}")
        )

        logo.save(image)

        with app.app_context():
            msg = Message(sender=app.config.get("MAIL_USERNAME"), recipients=[f'<{app.config.get("MAIL_USERNAME")}>'])
            msg.subject = "Request to join Pighub"
            msg.html = render_template("email.html", details=details, image=image)
            mail.send(msg)

        return redirect(url_for('shopPage'))


@app.route('/admin')
def adminPage():
    return render_template("admin.html")


@app.route('/reset/<string:name>')
def reset(name):
    try:
        conn = connect("retailers.db")
        conn.execute('delete from companies where name==?;', [name.upper()])
        conn.commit()
        conn.execute('vacuum;')
        conn.commit()
    except OperationalError as e:
        return f'<h1><b>There was an error empting the database</b><br>Reason->{e}</h1>'
    return redirect(url_for('index'))


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == "POST":
        name = request.form['name']
        addr = request.form['address']
        prod = request.form['products']
        serv = request.form['services']
        logo = request.form['logo']
        try:
            conn = connect("retailers.db")
            conn.execute('insert into companies values (?,?,?,?,?)', [name.upper(), addr, prod, serv, logo])
            conn.commit()
        except OperationalError as e:
            return f'<h1><b>There was an error inserting values into database</b><br>Reason->{e}</h1>'
        return redirect(url_for('shopPage'))


if __name__ == '__main__':
    app.run("0.0.0.0")
