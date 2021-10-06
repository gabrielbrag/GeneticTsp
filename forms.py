from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField

class CreateRoute(FlaskForm):
    gen = IntegerField("Gerações")
    submit = SubmitField('Criar Rota')