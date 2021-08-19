From flask import Flask, render_template, redirect, url_for, jsonify, make_response, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField

app = Flask("__name__")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'moj_klucz'
boot = Bootstrap(app)
db = SQLAlchemy(app)


# model rekordu plytowego

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(200), nullable=False)
    date_of_record = db.Column(db.String(10), nullable=False)


class RecordForm(FlaskForm):
    name_of_author = StringField('Podaj imie autora plyty')
    year_of_record = StringField('Podaj rok wydania plyty')
    submit = SubmitField('Dodaj rekord')


class UpdateRecordForm(FlaskForm):
    name_of_author = StringField('Zmien nazwe autora')
    year_of_record = StringField('Zmien rok powstania plyty')
    submit = SubmitField('Wykonaj update')


@app.route('/', methods=['POST', 'GET'])
def index():
    form = RecordForm()
    if form.validate_on_submit():
        name = form.name_of_author.data
        year = form.year_of_record.data
        record = Record(author=name, date_of_record=year)
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        records = Record.query.all()
    return render_template('records.html', form=form, records=records)


@app.route('/records/delete/<int:id>')
def delete_record(id):
    record_to_delete = Record.query.get_or_404(id)
    db.session.delete(record_to_delete)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/records/update/<int:id>', methods=['POST', 'GET'])
def update_record(id):
    record_to_update = Record.query.get_or_404(id)
    form_update = UpdateRecordForm()
    if form_update.validate_on_submit():
        record_to_update.author = form_update.name_of_author.data
        record_to_update.date_of_record = form_update.year_of_record.data
        db.session.commit()
        return redirect('/')
    else:
        return render_template('update.html', form=form_update)


######API DO MOJEJ APLIKACJI #############

@app.route('/api/records', methods=['GET'])
def get_all_records():
    records = Record.query.all()
    total = len(records)
    output = []
    for record in records:
        record_data = {}
        record_data['id'] = record.id
        record_data['author'] = record.author
        record_data['year'] = record.date_of_record
        output.append(record_data)

    response = jsonify(
        {
            "total": total,
            "items":
                output
        }
    )
    return response, 200


@app.route('/api/records', methods=['POST'])
def create_task():
    data = request.get_json()
    new_task = Record(author=data['author'], date_of_record=data['date_of_record'])
    db.session.add(new_task)
    db.session.commit()
    return make_response(jsonify("New task is created!"), 200)


@app.route('/api/records/<int:id>', methods=['GET'])
def get_one_record(id):
    record = Record.query.filter_by(id=id).first()
    if not record:
        return make_response(jsonify("id not found"), 404)
    result = {"author": record.author, "year": record.date_of_record}
    return make_response(jsonify(result), 200)


@app.route("/api/records/<int:id>", methods=["DELETE"])
def delete_one_record(id):
    record = Record.query.filter_by(id=id).first()

    if not record:
        return make_response(jsonify("Task id not found"), 404)

    db.session.delete(record)
    db.session.commit()
    return make_response(jsonify("Deleted!"), 200)


@app.route("/api/records/<int:id>", methods=["PUT"])
def modify_one_record(id):
    data = request.get_json()
    name = data['author']
    date = data['date_of_record']
    record = Record.query.get_or_404(id)
    record.author = name
    record.date_of_record = date
    db.session.commit()
    return make_response(jsonify("Task updated!"), 200)


if __name__ == '__main__':
    app.run()