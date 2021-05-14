from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from random import choice

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, DecimalField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

## Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = 'kanishka'
Bootstrap(app)


## Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)

        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route('/random')
def random():
    cafes = db.session.query(Cafe).all()
    c = choice(cafes)
    print(c)

    return jsonify(cafe=c.to_dict())


@app.route('/all')
def all():
    all_cafes = db.session.query(Cafe).all()
    List = []
    for cafe in all_cafes:
        List.append(cafe.to_dict())

    return jsonify(cafe=List)


def make_bool(val: int) -> bool:
    return bool(int(val))


# this is how we create the search parameter.
@app.route("/search")
def search():
    # we use request.args.get() to get the GET request,while we use request.form.get() to get POST data.
    query_location = request.args.get('loc')
    cafes = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafes:
        return jsonify(cafe=cafes.to_dict())
    else:
        return jsonify(error={"Not found": 'Sorry,we don\'t have a cafe at that location'})


## HTTP POST - Create Record
@app.route('/add', methods=['GET', 'POST'])
def add():
    new_cafe = Cafe(name=request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    has_sockets=make_bool(request.form.get('has_sockets')),
                    has_toilet=make_bool(request.form.get('has_toilet')),
                    has_wifi=make_bool(request.form.get('has_wifi')),
                    can_take_calls=make_bool(request.form.get('can_take_calls')),
                    seats=request.form.get('seats'),
                    coffee_price=request.form.get('coffee_price'))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": 'Successfully added the new cafe.'})


# always change the methods otherwise the code won't work.
## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['GET', 'PATCH'])
def update(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        print('found id')
        cafe_to_update = Cafe.query.get(cafe_id)
        cafe_to_update.coffee_price = request.args.get('new_price')
        db.session.commit()
        # to add the status code just enter the (,) status code" at the end of return statement.
        return jsonify(response={'message': 'Successfully updated price'}), 200
    else:
        return jsonify(error={"Not found": 'Sorry,a cafe with that id is not found in the database.'}), 404


## HTTP DELETE - Delete Record
@app.route('/report-closed/<int:cafe_id>', methods=['GET', 'DELETE'])
def delete(cafe_id):
    cafe = db.session.query(Cafe).filter_by(id=cafe_id).first()
    if cafe:
        if request.args.get('api-key') == 'TopSecretAPIKey':
            cafe_to_delete = Cafe.query.get(cafe_id)
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={'message': 'Successfully deleted the cafe.'}), 200
        else:
            return jsonify({'Error': 'Sorry, that\'s not allowed. Make sure you have the correct api_key.'}), 403
    else:
        return jsonify(error={'Not found': 'Sorry,a cafe with that id is not found in the database.'}), 404


if __name__ == '__main__':
    app.run(debug=True)
