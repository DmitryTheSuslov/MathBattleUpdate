from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired


class NewTaskForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    short_description = TextAreaField('Краткое содержание', validators=[DataRequired()])
    content = TextAreaField('Полное содержание', validators=[DataRequired()])
    submit = SubmitField('Добавить')
