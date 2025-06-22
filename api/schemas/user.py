"""
User schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class UserSchema(Schema):
    """Schema for user data validation and serialization"""
    id = fields.String(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.String(load_only=True, validate=validate.Length(min=8))
    first_name = fields.String(validate=validate.Length(max=50))
    last_name = fields.String(validate=validate.Length(max=50))
    role = fields.String(validate=validate.OneOf(["user", "admin"]), dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates("password")
    def validate_password(self, value):
        """Validate password complexity"""
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r"[0-9]", value):
            raise ValidationError("Password must contain at least one number")

class UserLoginSchema(Schema):
    """Schema for user login validation"""
    username = fields.String()
    email = fields.Email()
    password = fields.String(required=True)
    
    @validates("email")
    def validate_email_or_username(self, value, **kwargs):
        """Validate that either email or username is provided"""
        if not value and not kwargs.get("data", {}).get("username"):
            raise ValidationError("Either email or username must be provided")

class UserRegisterSchema(UserSchema):
    """Schema for user registration validation"""
    password = fields.String(required=True, validate=validate.Length(min=8))
    password_confirm = fields.String(required=True)
    
    @validates("password_confirm")
    def validate_password_match(self, value, **kwargs):
        """Validate that passwords match"""
        if value != kwargs.get("data", {}).get("password"):
            raise ValidationError("Passwords must match")