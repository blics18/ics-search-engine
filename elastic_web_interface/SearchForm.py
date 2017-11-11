from wtforms import Form, BooleanField, StringField, PasswordField, validators

class SearchForm(Form):
    query = StringField('')
