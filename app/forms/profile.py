from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import Optional, Length, DataRequired

COUNTRIES = [
    ('UN', 'Global / Unspecified'),
    ('US', 'United States'),
    ('GB', 'United Kingdom'),
    ('JP', 'Japan'),
    ('BR', 'Brazil'),
    ('FR', 'France'),
    ('DE', 'Germany'),
    ('ES', 'Spain'),
    ('IT', 'Italy'),
    ('AR', 'Argentina'),
    ('PT', 'Portugal'),
    ('NL', 'Netherlands'),
    ('TR', 'Turkey'),
    ('ID', 'Indonesia'),
    ('MY', 'Malaysia'),
    ('KR', 'South Korea'),
    ('SA', 'Saudi Arabia'),
    ('EG', 'Egypt'),
    ('NG', 'Nigeria'),
    ('MX', 'Mexico'),
    ('CO', 'Colombia'),
]

class ProfileForm(FlaskForm):
    display_name = StringField('Display Name', validators=[
        Optional(),
        Length(max=50)
    ], render_kw={"placeholder": "e.g. Captain Kane"})
    
    efootball_id = StringField('eFootball In-Game ID / Konami ID', validators=[
        Optional(),
        Length(max=64)
    ], render_kw={"placeholder": "e.g. 123-456-789 or Konami Account Tag"})
    
    bio = TextAreaField('Player Bio / Team Notes', validators=[
        Optional(),
        Length(max=280)
    ], render_kw={"rows": 3, "placeholder": "Division 1 grinder, Epics collector..."})
    
    country = SelectField('Country / Region', choices=COUNTRIES, default='UN')
    
    avatar = FileField('Upload Custom Avatar', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (.jpg, .png, .webp)')
    ])
    
    is_private = BooleanField('Hide my vault from public leaderboards & search')
    
    submit = SubmitField('Save Profile Settings')


class ApiTokenForm(FlaskForm):
    name = StringField('Token Label / Device Name', validators=[
        DataRequired(message='Provide a label for this API token (e.g. Chrome Tampermonkey).'),
        Length(max=60)
    ], render_kw={"placeholder": "e.g. Tampermonkey Chrome Extension"})
    
    submit = SubmitField('Generate Secret Bearer Token')
