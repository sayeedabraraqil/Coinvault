from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length

class LogCoinForm(FlaskForm):
    amount = IntegerField('Current Coin Amount', validators=[
        DataRequired(message='Enter your current coin balance.'),
        NumberRange(min=0, max=20_000_000, message='Amount must be non-negative and under 20,000,000.')
    ], render_kw={"placeholder": "e.g. 14,850", "autocomplete": "off"})
    
    note = StringField('Transaction / Snapshot Note', validators=[
        Optional(),
        Length(max=200, message='Note must be 200 characters or fewer.')
    ], render_kw={"placeholder": "e.g. Completed Spanish League Tour, Match Pass claimed"})
    
    logged_at = DateTimeLocalField('Snapshot Date/Time (Optional Backdate)', format='%Y-%m-%dT%H:%M', validators=[
        Optional()
    ])
    
    submit = SubmitField('Commit Balance to Vault')


class EditCoinForm(FlaskForm):
    amount = IntegerField('Corrected Coin Amount', validators=[
        DataRequired(),
        NumberRange(min=0, max=20_000_000)
    ])
    note = StringField('Edit Reason / Note', validators=[
        Optional(),
        Length(max=200)
    ])
    submit = SubmitField('Update Snapshot')
