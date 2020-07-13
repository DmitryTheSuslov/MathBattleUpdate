from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewAnswerForm(FlaskForm):
    answer_field = StringField('Сообщение...', validators=[DataRequired()])
    submit = SubmitField('Отправить')
