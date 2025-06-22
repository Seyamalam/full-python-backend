"""
BlogPost schemas for validation and serialization
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class BlogPostSchema(Schema):
    """Schema for blog post data validation and serialization"""
    id = fields.String(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(min=3, max=200))
    slug = fields.String(validate=validate.Length(min=3, max=200))
    content = fields.String(required=True)
    summary = fields.String()
    featured_image = fields.URL()
    author_id = fields.String(dump_only=True)
    author = fields.String(dump_only=True)
    status = fields.String(validate=validate.OneOf(["draft", "published", "archived"]))
    view_count = fields.Integer(dump_only=True)
    is_featured = fields.Boolean()
    tags = fields.List(fields.String())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(dump_only=True)
    
    @validates("slug")
    def validate_slug(self, value):
        """Validate slug format"""
        if not value:
            return
            
        if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", value):
            raise ValidationError("Slug must contain only lowercase letters, numbers, and hyphens")