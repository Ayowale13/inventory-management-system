"""WTForms definitions."""
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, DecimalField,
                     IntegerField, BooleanField, SubmitField, TextAreaField, HiddenField)
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 80)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(3, 80)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    full_name = StringField("Full Name", validators=[Optional(), Length(0, 120)])
    role = SelectField("Role", choices=[("staff", "Staff"), ("admin", "Admin")])
    password = PasswordField("Password", validators=[Optional(), Length(6, 128)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(1, 150)])
    category = StringField("Category", validators=[Optional(), Length(0, 80)])
    cost_price = DecimalField("Cost Price", validators=[DataRequired(), NumberRange(min=0)])
    selling_price = DecimalField("Selling Price", validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=0)])
    min_stock = IntegerField("Minimum Stock Level",
                             validators=[DataRequired(), NumberRange(min=0)], default=5)
    submit = SubmitField("Save Product")


class SaleForm(FlaskForm):
    product_id = HiddenField(validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Record Sale")


class RestockForm(FlaskForm):
    product_id = HiddenField(validators=[DataRequired()])
    quantity_added = IntegerField("Quantity to Add",
                                  validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Restock")


class CustomFieldForm(FlaskForm):
    name = StringField("Internal Name (no spaces)",
                       validators=[DataRequired(), Length(1, 80)])
    label = StringField("Display Label", validators=[DataRequired(), Length(1, 120)])
    field_type = SelectField("Field Type", choices=[
        ("text", "Text"), ("number", "Number"),
        ("date", "Date"), ("boolean", "Yes/No"),
    ])
    is_visible = BooleanField("Visible in table", default=True)
    sort_order = IntegerField("Sort Order", default=0)
    submit = SubmitField("Save Field")
