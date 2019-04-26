from wtforms import Form, StringField, PasswordField, RadioField, validators

class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=90)])
    username = StringField("Username", [validators.Length(min=6, max=30)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", [
        validators.Length(min=6, max=100),
        validators.DataRequired()
    ])
    confirm = PasswordField("Confirm Password", [
        validators.EqualTo("password", message="Passwords do not match.")
    ])

class LoginForm(Form):
    username = StringField("Username", [validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])