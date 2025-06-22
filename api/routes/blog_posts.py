"""
Blog post management routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import re
import datetime

from api.extensions import db, limiter
from api.models import BlogPost, User
from api.schemas import BlogPostSchema
from api.utils.decorators import admin_required

blog_posts_bp = Blueprint("blog_posts", __name__)

def slugify(text):
    """Convert text to slug format"""
    # Convert to lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove special characters
    text = re.sub(r'[^a-z0-9\-]', '', text)
    # Remove duplicate hyphens
    text = re.sub(r'-+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text

@blog_posts_bp.route("", methods=["GET"])
@limiter.limit("60 per minute")
def get_blog_posts():
    """
    Get all blog posts
    ---
    tags:
      - Blog
    parameters:
      - in: query
        name: page
        schema:
          type: integer
          default: 1
      - in: query
        name: per_page
        schema:
          type: integer
          default: 10
      - in: query
        name: status
        schema:
          type: string
      - in: query
        name: tag
        schema:
          type: string
      - in: query
        name: featured
        schema:
          type: boolean
    responses:
      200:
        description: List of blog posts
    """
    try:
        # Get query parameters
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 10, type=int), 100)
        status = request.args.get("status", "published")
        tag = request.args.get("tag")
        featured = request.args.get("featured", type=bool)
        
        # Build query
        query = BlogPost.query
        
        # Filter by status (non-admins can only see published posts)
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        current_user = User.query.get(current_user_id) if current_user_id else None
        
        if not current_user or current_user.role != "admin":
            query = query.filter_by(status="published")
        elif status:
            query = query.filter_by(status=status)
        
        # Filter by tag
        if tag:
            query = query.filter(BlogPost.tags.like(f"%{tag}%"))
        
        # Filter by featured
        if featured is not None:
            query = query.filter_by(is_featured=featured)
        
        # Order by published_at desc
        query = query.order_by(BlogPost.published_at.desc())
        
        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page)
        
        # Return paginated results
        return jsonify({
            "blog_posts": [post.to_dict() for post in pagination.items],
            "total": pagination.total,
            "pages": pagination.pages,
            "page": page,
            "per_page": per_page
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@blog_posts_bp.route("/<post_id>", methods=["GET"])
def get_blog_post(post_id):
    """
    Get blog post by ID
    ---
    tags:
      - Blog
    parameters:
      - in: path
        name: post_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Blog post details
      404:
        description: Blog post not found
    """
    try:
        # Find blog post by ID
        post = BlogPost.query.get(post_id)
        if not post:
            return jsonify({"error": "Blog post not found"}), 404
        
        # Check if post is published or user is admin
        current_user_id = get_jwt_identity() if request.headers.get('Authorization') else None
        current_user = User.query.get(current_user_id) if current_user_id else None
        
        if post.status != "published" and (not current_user or current_user.role != "admin"):
            return jsonify({"error": "Blog post not found"}), 404
        
        # Increment view count
        post.view_count += 1
        db.session.commit()
        
        # Return post details
        return jsonify({
            "blog_post": post.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@blog_posts_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_blog_post():
    """
    Create a new blog post (admin only)
    ---
    tags:
      - Blog
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: blog_post
        schema:
          type: object
          required:
            - title
            - content
          properties:
            title:
              type: string
            content:
              type: string
            summary:
              type: string
            featured_image:
              type: string
            status:
              type: string
              enum: [draft, published, archived]
            is_featured:
              type: boolean
            tags:
              type: array
              items:
                type: string
    responses:
      201:
        description: Blog post created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        
        # Validate request data
        schema = BlogPostSchema()
        data = schema.load(request.json)
        
        # Generate slug from title if not provided
        slug = data.get("slug")
        if not slug:
            slug = slugify(data["title"])
            
        # Check if slug already exists
        existing_post = BlogPost.query.filter_by(slug=slug).first()
        if existing_post:
            # Append a unique identifier to make slug unique
            slug = f"{slug}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Process tags
        tags = data.get("tags", [])
        tags_str = ",".join(tags) if tags else ""
        
        # Set published_at if status is published
        published_at = None
        if data.get("status") == "published":
            published_at = datetime.datetime.utcnow()
        
        # Create new blog post
        post = BlogPost(
            title=data["title"],
            slug=slug,
            content=data["content"],
            summary=data.get("summary"),
            featured_image=data.get("featured_image"),
            author_id=current_user_id,
            status=data.get("status", "draft"),
            is_featured=data.get("is_featured", False),
            tags=tags_str,
            published_at=published_at
        )
        
        # Save to database
        db.session.add(post)
        db.session.commit()
        
        # Return created post
        return jsonify({
            "message": "Blog post created successfully",
            "blog_post": post.to_dict()
        }), 201
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
        
@blog_posts_bp.route("/<post_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_blog_post(post_id):
    """
    Update blog post by ID (admin only)
    ---
    tags:
      - Blog
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: post_id
        schema:
          type: string
        required: true
      - in: body
        name: blog_post
        schema:
          type: object
          properties:
            title:
              type: string
            content:
              type: string
            summary:
              type: string
            featured_image:
              type: string
            status:
              type: string
              enum: [draft, published, archived]
            is_featured:
              type: boolean
            tags:
              type: array
              items:
                type: string
    responses:
      200:
        description: Blog post updated successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Blog post not found
    """
    try:
        # Find blog post by ID
        post = BlogPost.query.get(post_id)
        if not post:
            return jsonify({"error": "Blog post not found"}), 404
        
        # Validate request data
        schema = BlogPostSchema(partial=True)
        data = schema.load(request.json)
        
        # Check if title changed and update slug if needed
        if "title" in data and data["title"] != post.title:
            slug = slugify(data["title"])
            
            # Check if slug already exists
            existing_post = BlogPost.query.filter(
                BlogPost.slug == slug,
                BlogPost.id != post_id
            ).first()
            
            if existing_post:
                # Append a unique identifier to make slug unique
                slug = f"{slug}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                
            post.slug = slug
        
        # Process tags if provided
        if "tags" in data:
            tags = data.get("tags", [])
            post.tags = ",".join(tags) if tags else ""
        
        # Update published_at if status changed to published
        if "status" in data and data["status"] == "published" and post.status != "published":
            post.published_at = datetime.datetime.utcnow()
        
        # Update other fields
        for key, value in data.items():
            if key != "tags":  # Tags already processed
                setattr(post, key, value)
        
        # Save to database
        db.session.commit()
        
        # Return updated post
        return jsonify({
            "message": "Blog post updated successfully",
            "blog_post": post.to_dict()
        }), 200
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@blog_posts_bp.route("/<post_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_blog_post(post_id):
    """
    Delete blog post by ID (admin only)
    ---
    tags:
      - Blog
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: post_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Blog post deleted successfully
      401:
        description: Unauthorized
      403:
        description: Forbidden - Admin access required
      404:
        description: Blog post not found
    """
    try:
        # Find blog post by ID
        post = BlogPost.query.get(post_id)
        if not post:
            return jsonify({"error": "Blog post not found"}), 404
        
        # Delete blog post
        db.session.delete(post)
        db.session.commit()
        
        # Return success message
        return jsonify({
            "message": "Blog post deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@blog_posts_bp.route("/tags", methods=["GET"])
def get_tags():
    """
    Get all blog post tags
    ---
    tags:
      - Blog
    responses:
      200:
        description: List of blog post tags
    """
    try:
        # Get all tags from published posts
        posts = BlogPost.query.filter_by(status="published").all()
        
        # Extract and flatten tags
        all_tags = []
        for post in posts:
            if post.tags:
                all_tags.extend(post.tags.split(","))
        
        # Count occurrences of each tag
        tag_counts = {}
        for tag in all_tags:
            tag = tag.strip()
            if tag:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort tags by count (descending)
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return tags with counts
        return jsonify({
            "tags": [{"name": tag, "count": count} for tag, count in sorted_tags]
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500