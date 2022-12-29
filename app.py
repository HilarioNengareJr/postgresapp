import os
from flask import Flask, render_template,redirect, session, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sqlalchemy.engine import URL

# an instance of flask app
app = Flask(__name__)

uri = URL.create(
    drivername="postgresql",
    username=os.environ.get("POSTGRES_USER"),
    host=os.environ.get("POSTGRES_HOST"),
    database="postgres",
)

# secret key configuration
app.config['SECRET_KEY'] = 'sickrat'
# my uri for postgres database
app.config['SQLALCHEMY_DATABASE_URI'] = uri

db = SQLAlchemy(app)

# class objects for student
# instructor and advisor
class Student(db.Model):
    __tablename__ = 'student'
    std_id = db.Column(db.String(20), primary_key=True)
    std_name = db.Column(db.String(100), unique=True, nullable=False)
    std_email = db.Column(db.String(120), unique=True, nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)

# set nullable to false
# meaning it cannot be empty


class Instructor(db.Model):
    __tablename__ = 'instructor'
    ins_id = db.Column(db.String(20), primary_key=True)
    ins_name = db.Column(db.String(100), unique=True, nullable=False)
    ins_email = db.Column(db.String(120), unique=True, nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)


class Advisor(db.Model):
    adv_id = db.Column( db.String(20), db.ForeignKey('instructor.ins_id'),primary_key=True, nullable=False)
    st_id =db.Column(db.String(20), db.ForeignKey('student.std_id'), nullable=False)

# forms


class StudentInsertionForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Student Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Student Email',
                        validators=[DataRequired(), Email()])
    dept_name = StringField('Department', validators=[DataRequired()])
    submit = SubmitField('Add Student')


class InstructorInsertionForm(FlaskForm):
    ins_id = StringField('Instructor ID', validators=[DataRequired()])
    name = StringField('Instructor Name',
                           validators=[DataRequired(), Length(min=2, max=35)])
    email = StringField('Instructor Email ',
                        validators=[DataRequired(), Email()])
    dept_name = StringField('Department', validators=[DataRequired()])
    submit = SubmitField('Add Instructor')


class AdvisorInsertionForm(FlaskForm):
    ins_id = StringField('Instructor ID', validators=[DataRequired()])
    std_id = StringField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Add Advisor')

class StudentLookUpForm(FlaskForm):
    search = StringField('Perform Search', validators=[DataRequired(), Length(max=60)])
    submit = SubmitField('Search')
# routes


@app.route('/', methods=['GET', 'POST'])
def menu():
    return render_template('menu.html', title='menu')


@app.route("/InsertingStudent", methods=['GET', 'POST'])
def student():
    form = StudentInsertionForm()
    if form.validate_on_submit():
         student = Student(std_id=form.student_id.data, std_name=form.name.data,
                           std_email=form.email.data, dept_name=form.dept_name.data)
         db.session.add(student)
         db.session.commit()
         flash('Student has been added successfully! ', 'success')
         return redirect(url_for('menu'))
    return render_template('student.html', title='insert student', form=form)

# routes
@app.route("/InsertingInstructor", methods=['GET', 'POST'])
def instructor():
    form = InstructorInsertionForm()
    if form.validate_on_submit():
         instructor = Instructor(ins_id = form.ins_id.data, ins_name=form.name.data, ins_email=form.email.data, dept_name=form.dept_name.data)
         db.session.add(instructor)
         db.session.commit()
         flash('Instructor has been added successfully!','success')
         return redirect(url_for('menu'))
    return render_template('instructor.html', title='Instructor Insertion', form=form)

     # routes
@app.route("/InsertingAdvisor", methods=['GET', 'POST'])
def advisor():
    form = AdvisorInsertionForm()
    if form.validate_on_submit():
         advisor = Advisor(adv_id=form.ins_id.data,st_id=form.std_id.data)
         db.session.add(advisor)
         db.session.commit()
         flash('Advisor appointed successfully!','success')
         return redirect(url_for('menu'))
    return render_template('advisor.html', title='Advisor Insertion', form=form)


@app.route("/StudentSearch",methods=['GET','POST'])
def student_lookup():
    form = StudentLookUpForm()
    results = Student.query

    if form.validate_on_submit():
        results = results.filter(Student.std_name.like('%' + form.search.data + '%'))
    results = results.order_by(Student.std_name).all() 

    return render_template('studentlookup.html',results=results, form=form)

@app.route("/InstructorSearch",methods=['GET','POST'])
def instructor_lookup():
    form = InstructorLookUpForm()
    results = Student.query

    if form.validate_on_submit():
        results = results.filter(Instructor.ins_name.like('%' + form.search.data + '%')) 


    results = results.order_by(Instructor.ins_name).all() 

    return render_template('instructorlookup.html',results=results, form=form)

if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():  
        db.create_all()
    
