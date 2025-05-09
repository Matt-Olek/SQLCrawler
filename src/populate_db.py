import random
from faker import Faker
from db_utility import PostgresDB

# Initialize Faker
fake = Faker()

def create_tables(db):
    """Create necessary tables for the mock database"""
    # Users table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, fetch=False)
    
    # Products table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """, fetch=False)
    
    # Orders table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount DECIMAL(10, 2) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending'
        )
    """, fetch=False)
    
    # Order Items table
    db.execute_query("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )
    """, fetch=False)
    
    print("Tables created successfully")

def populate_users(db, num_users=50):
    """Populate users table with fake data"""
    users = []
    for _ in range(num_users):
        username = fake.user_name()
        email = fake.email()
        first_name = fake.first_name()
        last_name = fake.last_name()
        date_joined = fake.date_time_between(start_date='-2y', end_date='now')
        
        result = db.execute_query(
            """
            INSERT INTO users (username, email, first_name, last_name, date_joined) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            [username, email, first_name, last_name, date_joined]
        )
        
        if result:
            user_id = result[0][0]
            users.append(user_id)
    
    print(f"Added {len(users)} users")
    return users

def populate_products(db, num_products=100):
    """Populate products table with fake data"""
    products = []
    categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Beauty', 'Sports', 'Food']
    
    for _ in range(num_products):
        name = fake.word()
        description = fake.paragraph()
        price = round(random.uniform(9.99, 999.99), 2)
        category = random.choice(categories)
        created_at = fake.date_time_between(start_date='-1y', end_date='now')
        
        result = db.execute_query(
            """
            INSERT INTO products (name, description, price, category, created_at) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            [name, description, price, category, created_at]
        )
        
        if result:
            product_id = result[0][0]
            products.append(product_id)
    
    print(f"Added {len(products)} products")
    return products

def populate_orders(db, user_ids, product_ids, num_orders=200):
    """Populate orders and order_items tables with fake data"""
    order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    
    for _ in range(num_orders):
        user_id = random.choice(user_ids)
        order_date = fake.date_time_between(start_date='-6m', end_date='now')
        status = random.choice(order_statuses)
        
        # Create between 1 and 5 order items
        num_items = random.randint(1, 5)
        selected_products = random.sample(product_ids, min(num_items, len(product_ids)))
        
        total_amount = 0
        order_items = []
        
        for product_id in selected_products:
            quantity = random.randint(1, 3)
            # Get product price
            price_result = db.execute_query(
                "SELECT price FROM products WHERE id = %s",
                [product_id]
            )
            if price_result:
                price = price_result[0][0]
                item_total = price * quantity
                total_amount += item_total
                order_items.append((product_id, quantity, price))
        
        # Insert order
        order_result = db.execute_query(
            """
            INSERT INTO orders (user_id, order_date, total_amount, status) 
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            [user_id, order_date, total_amount, status]
        )
        
        if order_result:
            order_id = order_result[0][0]
            
            # Insert order items
            for product_id, quantity, price in order_items:
                db.execute_query(
                    """
                    INSERT INTO order_items (order_id, product_id, quantity, price) 
                    VALUES (%s, %s, %s, %s)
                    """,
                    [order_id, product_id, quantity, price],
                    fetch=False
                )
    
    print(f"Added {num_orders} orders with items")

def main():
    # Connect to the database
    db = PostgresDB()
    db.connect()
    
    # Create tables
    create_tables(db)
    
    # Populate tables
    user_ids = populate_users(db)
    product_ids = populate_products(db)
    populate_orders(db, user_ids, product_ids)
    
    # Close connection
    db.close()
    
    print("Database successfully populated with mock data!")

if __name__ == "__main__":
    main() 