"""
Custom CLI commands for the Flask application
"""
import click
import random
from flask.cli import with_appcontext
from faker import Faker
import datetime

from api.extensions import db
from api.models import User, Product, Order, OrderItem, BlogPost

fake = Faker()

@click.command("seed-db")
@click.option("--users", default=10, help="Number of users to create")
@click.option("--products", default=50, help="Number of products to create")
@click.option("--orders", default=20, help="Number of orders to create")
@click.option("--posts", default=30, help="Number of blog posts to create")
@with_appcontext
def seed_database(users, products, orders, posts):
    """Seed the database with sample data"""
    click.echo("Seeding database...")
    
    # Create admin user if not exists
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True
        )
        admin.password = "Admin123!"
        db.session.add(admin)
        click.echo("Created admin user: admin@example.com / Admin123!")
    
    # Create regular users
    click.echo(f"Creating {users} users...")
    created_users = [admin]
    for i in range(users):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
        email = f"{username}@{fake.domain_name()}"
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role="user",
            is_active=True
        )
        user.password = "User123!"
        db.session.add(user)
        created_users.append(user)
    
    # Create products
    click.echo(f"Creating {products} products...")
    categories = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Sports", "Toys", "Beauty", "Automotive"]
    created_products = []
    
    for i in range(products):
        category = random.choice(categories)
        price = round(random.uniform(9.99, 999.99), 2)
        
        product = Product(
            name=fake.catch_phrase(),
            description=fake.paragraph(nb_sentences=5),
            price=price,
            stock=random.randint(0, 100),
            category=category,
            image_url=f"https://picsum.photos/id/{random.randint(1, 1000)}/500/500",
            is_active=random.random() > 0.1  # 90% active
        )
        db.session.add(product)
        created_products.append(product)
    
    # Commit to get IDs
    db.session.commit()
    
    # Create blog posts
    click.echo(f"Creating {posts} blog posts...")
    statuses = ["draft", "published", "archived"]
    weights = [0.2, 0.7, 0.1]  # 20% draft, 70% published, 10% archived
    
    for i in range(posts):
        status = random.choices(statuses, weights=weights)[0]
        author = random.choice(created_users)
        title = fake.sentence(nb_words=6)
        
        # Generate slug from title
        slug = title.lower().replace(" ", "-")
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # Add random tags
        tag_count = random.randint(1, 5)
        tags = []
        for _ in range(tag_count):
            tags.append(fake.word())
        
        published_at = None
        if status == "published":
            published_at = fake.date_time_between(start_date="-1y", end_date="now")
        
        # Generate paragraphs and join them with newlines
        paragraphs = fake.paragraphs(nb=random.randint(3, 10))
        content = "\n\n".join(paragraphs)
        
        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            summary=fake.paragraph(nb_sentences=2),
            featured_image=f"https://picsum.photos/id/{random.randint(1, 1000)}/800/400",
            author_id=author.id,
            status=status,
            view_count=random.randint(0, 1000) if status == "published" else 0,
            is_featured=random.random() < 0.2,  # 20% featured
            tags=",".join(tags),
            published_at=published_at
        )
        db.session.add(post)
    
    # Create orders
    click.echo(f"Creating {orders} orders...")
    statuses = ["pending", "processing", "completed", "cancelled"]
    payment_methods = ["credit_card", "paypal", "bank_transfer"]
    payment_statuses = ["unpaid", "paid", "refunded"]
    
    for i in range(orders):
        user = random.choice(created_users)
        status = random.choice(statuses)
        
        # Create order items (1-5 items per order)
        item_count = random.randint(1, 5)
        order_products = random.sample(created_products, item_count)
        
        total_amount = 0
        order_items = []
        
        for product in order_products:
            quantity = random.randint(1, 3)
            price = product.price
            total_amount += price * quantity
            
            order_item = OrderItem(
                product_id=product.id,
                quantity=quantity,
                price=price
            )
            order_items.append(order_item)
        
        # Create order
        order = Order(
            user_id=user.id,
            status=status,
            total_amount=round(total_amount, 2),
            shipping_address=fake.address(),
            payment_method=random.choice(payment_methods),
            payment_status=random.choice(payment_statuses),
            created_at=fake.date_time_between(start_date="-6M", end_date="now")
        )
        
        # Add items to order
        order.items = order_items
        db.session.add(order)
    
    # Commit all changes
    db.session.commit()
    click.echo("Database seeded successfully!")

@click.command("create-admin")
@click.argument("username")
@click.argument("email")
@click.password_option()
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user"""
    # Check if user already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        click.echo(f"Error: User with username '{username}' or email '{email}' already exists.")
        return
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        role="admin",
        is_active=True
    )
    admin.password = password
    
    # Save to database
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f"Admin user created successfully: {username} ({email})")

@click.command("run-tests")
@click.option("--coverage", is_flag=True, help="Run tests with coverage report")
@click.option("--verbose", is_flag=True, help="Run tests in verbose mode")
def run_tests(coverage, verbose):
    """Run the test suite"""
    import pytest
    
    args = []
    if verbose:
        args.append("-v")
    
    if coverage:
        args.extend(["--cov=api", "--cov-report=term", "--cov-report=html"])
    
    click.echo("Running tests...")
    result = pytest.main(args)
    
    if result == 0:
        click.echo("All tests passed!")
    else:
        click.echo("Tests failed!")

def register_commands(app):
    """Register custom commands with the Flask application"""
    app.cli.add_command(seed_database)
    app.cli.add_command(create_admin)
    app.cli.add_command(run_tests)