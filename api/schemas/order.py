"""
Order schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate

class OrderItemSchema(Schema):
    """Schema for order item data validation and serialization"""
    id = fields.String(dump_only=True)
    product_id = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Float(dump_only=True)
    product = fields.Nested("ProductSchema", dump_only=True)

class OrderSchema(Schema):
    """Schema for order data validation and serialization"""
    id = fields.String(dump_only=True)
    user_id = fields.String(dump_only=True)
    status = fields.String(validate=validate.OneOf(["pending", "processing", "completed", "cancelled"]))
    total_amount = fields.Float(dump_only=True)
    shipping_address = fields.String(required=True)
    payment_method = fields.String(required=True, validate=validate.OneOf(["credit_card", "paypal", "bank_transfer"]))
    payment_status = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema), required=True)