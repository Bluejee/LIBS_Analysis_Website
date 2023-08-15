from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, BooleanField  
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired

class PreInputForm(FlaskForm):
    imput_file = FileField('Data File',validators = [FileRequired()])
    # lower_wave = FloatField('lower wavelength',validators = [DataRequired()])
    # upper_wave = FloatField('lower wavelength', validators = [DataRequired()])
    # baseline_intensity = FloatField('baseline_intensity',validators = [DataRequired()])
    submit = SubmitField('Submit')

class InputForm(FlaskForm):
    imput_file = FileField('Data File',validators = [FileRequired()])
    lower_wave = FloatField('lower wavelength',validators = [DataRequired()])
    upper_wave = FloatField('lower wavelength', validators = [DataRequired()])
    baseline_intensity = FloatField('baseline_intensity',validators = [DataRequired()])
    submit = SubmitField('Submit')
    PS = BooleanField('')



