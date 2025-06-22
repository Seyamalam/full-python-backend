"""
BlogPost model definition
"""
import datetime
import uuid
from api.extensions import db

class BlogPost(db.Model):
    """Blog post model for content management"""
    __tablename__ = "blog_posts"
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    featured_image = db.Column(db.String(255), nullable=True)
    author_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), default="draft")  # draft, published, archived
    view_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    author = db.relationship("User", back_populates="blog_posts")
    
    def to_dict(self):
        """Convert blog post to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "content": self.content,
            "summary": self.summary,
            "featured_image": self.featured_image,
            "author_id": self.author_id,
            "author": self.author.username if self.author else None,
            "status": self.status,
            "view_count": self.view_count,
            "is_featured": self.is_featured,
            "tags": self.tags.split(",") if self.tags else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f"<BlogPost {self.title}>"