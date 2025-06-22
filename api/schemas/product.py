"""
Product schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate

class ProductSchema(Schema):
    """Schema for product data validation and serialization"""
    id = fields.String(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String()
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Integer(validate=validate.Range(min=0))
    category = fields.String(validate=validate.Length(max=50))
    image_url = fields.URL()
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)