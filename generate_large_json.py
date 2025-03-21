import os
import json
import random
import string
import uuid
from datetime import datetime, timedelta
import numpy as np
import math

# Configuration
JSON_FILES_DIR = r"C:\json_files"
NUM_FILES = 5
MIN_RECORDS_PER_FILE = 50000
MAX_RECORDS_PER_FILE = 250000

# Create directory if it doesn't exist
os.makedirs(JSON_FILES_DIR, exist_ok=True)

def random_date(start_date=datetime(2020, 1, 1), end_date=datetime.now()):
    """Generate a random date between start_date and end_date"""
    # Make sure end_date is after start_date
    if end_date <= start_date:
        # If dates are invalid, use a default range
        start_date = datetime(2020, 1, 1)
        end_date = datetime.now()
        
    delta = end_date - start_date
    # Make sure we have at least 1 day difference
    if delta.days < 1:
        delta = timedelta(days=1)
        
    random_days = random.randrange(delta.days)
    return start_date + timedelta(days=random_days)

def random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def generate_customer_data(num_records):
    """Generate a large dataset of customer data"""
    print(f"Generating customer dataset with {num_records} records...")
    
    customers = []
    
    # Create some base data to reference
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
              "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
              "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco"]
    
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ"]
    
    subscription_types = ["Basic", "Standard", "Premium", "Enterprise", "Trial"]
    
    status_options = ["Active", "Inactive", "Pending", "Suspended"]
    
    for i in range(num_records):
        # Generate a customer record
        first_name = random_string(8)
        last_name = random_string(10)
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        
        customer = {
            "id": str(uuid.uuid4()),
            "customer_number": f"CUST-{random.randint(10000, 99999)}",
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": {
                "street": f"{random.randint(100, 9999)} {random_string(8)} St",
                "city": random.choice(cities),
                "state": random.choice(states),
                "zip": f"{random.randint(10000, 99999)}",
                "country": "USA"
            },
            "registration_date": random_date().isoformat(),
            "status": random.choice(status_options),
            "subscription": {
                "type": random.choice(subscription_types),
                "price": round(random.uniform(9.99, 99.99), 2),
                "billing_cycle": random.choice(["Monthly", "Quarterly", "Annual"]),
                "auto_renew": random.choice([True, False]),
                "start_date": random_date().isoformat(),
                "end_date": random_date(start_date=datetime.now()).isoformat()
            },
            "preferences": {
                "notifications": random.choice([True, False]),
                "newsletter": random.choice([True, False]),
                "language": random.choice(["en", "es", "fr", "de", "zh"]),
                "theme": random.choice(["light", "dark", "system"])
            },
            "metrics": {
                "lifetime_value": round(random.uniform(100, 10000), 2),
                "orders": random.randint(0, 50),
                "site_visits": random.randint(1, 200),
                "average_order": round(random.uniform(10, 500), 2)
            },
            "tags": random.sample(["loyal", "new", "returning", "high-value", "potential", "inactive"], 
                                random.randint(0, 3))
        }
        
        # Add some purchases
        num_purchases = random.randint(0, 10)
        if num_purchases > 0:
            purchases = []
            for j in range(num_purchases):
                purchase = {
                    "id": f"ORD-{random.randint(100000, 999999)}",
                    "date": random_date().isoformat(),
                    "total": round(random.uniform(10, 1000), 2),
                    "items": random.randint(1, 10),
                    "status": random.choice(["Delivered", "Shipped", "Processing", "Cancelled"]),
                    "payment_method": random.choice(["Credit Card", "PayPal", "Bank Transfer"])
                }
                purchases.append(purchase)
            customer["purchases"] = purchases
        
        # Add to list
        customers.append(customer)
        
        # Show progress for large datasets
        if i > 0 and i % 10000 == 0:
            print(f"Generated {i} customer records...")
    
    print(f"Completed generating {len(customers)} customer records")
    return {
        "dataset_type": "customer_data",
        "generated": datetime.now().isoformat(),
        "record_count": len(customers),
        "data": customers
    }

def generate_product_catalog(num_records):
    """Generate a large product catalog"""
    print(f"Generating product catalog with {num_records} records...")
    
    products = []
    
    # Create some base data
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Toys", 
                 "Sports", "Automotive", "Health", "Beauty", "Grocery",
                 "Office", "Pet Supplies", "Garden", "Tools", "Industrial"]
    
    brands = ["TechMaster", "StyleHub", "HomeEssentials", "ReadMore", "PlayWorld",
              "ActiveLife", "AutoPro", "HealthFirst", "BeautyGlow", "FreshMart",
              "OfficePro", "PetPals", "GardenMaster", "ToolCraft", "IndustrialTech"]
    
    conditions = ["New", "Used", "Refurbished", "Open Box"]
    
    for i in range(num_records):
        # Generate random specifications based on category
        category = random.choice(categories)
        specs = {}
        
        if category == "Electronics":
            specs = {
                "processor": random.choice(["Intel i5", "Intel i7", "Intel i9", "AMD Ryzen 5", "AMD Ryzen 7"]),
                "memory": f"{random.choice([4, 8, 16, 32, 64])} GB",
                "storage": f"{random.choice([128, 256, 512, 1024, 2048])} GB",
                "screen_size": f"{round(random.uniform(5, 32), 1)}\"",
                "battery_life": f"{random.randint(2, 24)} hours"
            }
        elif category == "Clothing":
            specs = {
                "size": random.choice(["XS", "S", "M", "L", "XL", "XXL"]),
                "color": random.choice(["Red", "Blue", "Green", "Black", "White", "Yellow", "Purple"]),
                "material": random.choice(["Cotton", "Polyester", "Wool", "Silk", "Linen", "Denim"]),
                "gender": random.choice(["Men", "Women", "Unisex"]),
                "season": random.choice(["Spring", "Summer", "Fall", "Winter", "All Season"])
            }
        else:
            # Generic specs
            specs = {
                "dimension": f"{random.randint(1, 100)}x{random.randint(1, 100)}x{random.randint(1, 100)} cm",
                "weight": f"{round(random.uniform(0.1, 20), 2)} kg",
                "color": random.choice(["Red", "Blue", "Green", "Black", "White", "Yellow", "Purple"]),
                "warranty": f"{random.choice([1, 2, 3, 5])} years"
            }
        
        # Generate a product
        product = {
            "id": str(uuid.uuid4()),
            "sku": f"SKU-{random.randint(10000, 99999)}",
            "name": f"{random.choice(brands)} {random_string(8)} {random.randint(100, 999)}",
            "description": f"This is a {random.choice(['high-quality', 'premium', 'standard', 'budget'])} {category.lower()} product with {random.choice(['excellent', 'good', 'average'])} performance.",
            "category": category,
            "subcategory": f"{category}-{random.randint(1, 5)}",
            "brand": random.choice(brands),
            "model": f"Model-{random.randint(100, 999)}-{random_string(3)}",
            "price": round(random.uniform(9.99, 2999.99), 2),
            "discount": round(random.uniform(0, 0.5), 2),
            "condition": random.choice(conditions),
            "availability": random.choice([True, False]),
            "stock_quantity": random.randint(0, 1000),
            "specifications": specs,
            "ratings": {
                "average": round(random.uniform(1, 5), 1),
                "count": random.randint(0, 10000)
            },
            "tags": random.sample(["bestseller", "new", "sale", "featured", "limited", "eco-friendly", "premium"], 
                                random.randint(0, 3)),
            "created_at": random_date(start_date=datetime(2018, 1, 1)).isoformat(),
            "updated_at": random_date().isoformat()
        }
        
        # Add some images
        num_images = random.randint(1, 5)
        images = []
        for j in range(num_images):
            images.append({
                "url": f"https://example.com/products/{product['sku']}/image_{j+1}.jpg",
                "alt": f"Image {j+1} for {product['name']}",
                "is_primary": j == 0
            })
        product["images"] = images
        
        # Add to list
        products.append(product)
        
        # Show progress for large datasets
        if i > 0 and i % 10000 == 0:
            print(f"Generated {i} product records...")
    
    print(f"Completed generating {len(products)} product records")
    return {
        "dataset_type": "product_catalog",
        "generated": datetime.now().isoformat(),
        "record_count": len(products),
        "data": products
    }

def generate_transaction_data(num_records):
    """Generate a large transaction dataset"""
    print(f"Generating transaction dataset with {num_records} records...")
    
    transactions = []
    
    # Create some base data
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Apple Pay", "Google Pay", 
                       "Cryptocurrency", "Gift Card", "Store Credit", "Cash on Delivery"]
    
    status_options = ["Completed", "Pending", "Failed", "Refunded", "Cancelled", "Processing"]
    
    store_locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                       "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    
    # Product templates for line items
    product_templates = [
        {"name": "Laptop", "category": "Electronics", "price_range": (499, 2499)},
        {"name": "Smartphone", "category": "Electronics", "price_range": (199, 1299)},
        {"name": "T-Shirt", "category": "Clothing", "price_range": (9.99, 49.99)},
        {"name": "Jeans", "category": "Clothing", "price_range": (19.99, 99.99)},
        {"name": "Coffee Maker", "category": "Home & Kitchen", "price_range": (29.99, 199.99)},
        {"name": "Book", "category": "Books", "price_range": (4.99, 29.99)},
        {"name": "Action Figure", "category": "Toys", "price_range": (9.99, 49.99)},
        {"name": "Basketball", "category": "Sports", "price_range": (14.99, 79.99)},
        {"name": "Car Parts", "category": "Automotive", "price_range": (19.99, 299.99)},
        {"name": "Vitamins", "category": "Health", "price_range": (7.99, 59.99)}
    ]
    
    for i in range(num_records):
        # Transaction base info
        transaction_date = random_date()
        
        # Generate a transaction
        transaction = {
            "id": str(uuid.uuid4()),
            "transaction_number": f"TRX-{random.randint(100000, 999999)}",
            "date": transaction_date.isoformat(),
            "customer_id": f"CUST-{random.randint(10000, 99999)}",
            "store_id": f"STORE-{random.randint(100, 999)}",
            "store_location": random.choice(store_locations),
            "cashier_id": f"EMP-{random.randint(1000, 9999)}",
            "register_id": f"REG-{random.randint(10, 99)}",
            "payment_method": random.choice(payment_methods),
            "status": random.choice(status_options),
            "subtotal": 0,  # Will calculate from items
            "tax_rate": round(random.uniform(0.05, 0.12), 2),
            "tax_amount": 0,  # Will calculate
            "discount_amount": 0,  # Will calculate
            "total_amount": 0,  # Will calculate
            "currency": "USD",
            "is_online": random.choice([True, False]),
            "notes": "" if random.random() > 0.2 else f"Customer note: {random_string(20)}"
        }
        
        # Add line items
        num_items = random.randint(1, 10)
        items = []
        subtotal = 0
        
        for j in range(num_items):
            # Pick a random product template
            product = random.choice(product_templates)
            
            # Generate price within range
            price = round(random.uniform(product['price_range'][0], product['price_range'][1]), 2)
            quantity = random.randint(1, 5)
            item_total = price * quantity
            subtotal += item_total
            
            item = {
                "id": f"ITEM-{random.randint(10000, 99999)}",
                "product_id": f"PROD-{random.randint(10000, 99999)}",
                "name": f"{product['name']} {random_string(5)}",
                "category": product['category'],
                "price": price,
                "quantity": quantity,
                "discount_percentage": round(random.uniform(0, 0.3), 2) if random.random() > 0.7 else 0,
                "total": item_total
            }
            
            # Apply discount if any
            if item["discount_percentage"] > 0:
                discount = item_total * item["discount_percentage"]
                item["total"] -= discount
                transaction["discount_amount"] += discount
                subtotal -= discount
            
            items.append(item)
        
        # Calculate totals
        transaction["subtotal"] = round(subtotal, 2)
        transaction["tax_amount"] = round(transaction["subtotal"] * transaction["tax_rate"], 2)
        transaction["total_amount"] = round(transaction["subtotal"] + transaction["tax_amount"], 2)
        transaction["items"] = items
        
        # Add to list
        transactions.append(transaction)
        
        # Show progress for large datasets
        if i > 0 and i % 10000 == 0:
            print(f"Generated {i} transaction records...")
    
    print(f"Completed generating {len(transactions)} transaction records")
    return {
        "dataset_type": "transaction_data",
        "generated": datetime.now().isoformat(),
        "record_count": len(transactions),
        "data": transactions
    }

def generate_sensor_data(num_records):
    """Generate a large sensor reading dataset"""
    print(f"Generating sensor dataset with {num_records} records...")
    
    readings = []
    
    # Create some base data
    sensor_types = ["Temperature", "Humidity", "Pressure", "Light", "Motion", 
                    "CO2", "Voltage", "Current", "pH", "Vibration"]
    
    locations = ["Building A", "Building B", "Building C", "Warehouse", "Factory Floor", 
                "Office", "Exterior", "Data Center", "Clean Room", "Laboratory"]
    
    units = {
        "Temperature": "°C",
        "Humidity": "%",
        "Pressure": "hPa",
        "Light": "lux",
        "Motion": "binary",
        "CO2": "ppm",
        "Voltage": "V",
        "Current": "A",
        "pH": "pH",
        "Vibration": "Hz"
    }
    
    # Value ranges for each sensor type
    value_ranges = {
        "Temperature": (-20, 50),
        "Humidity": (0, 100),
        "Pressure": (970, 1050),
        "Light": (0, 10000),
        "Motion": (0, 1),
        "CO2": (300, 5000),
        "Voltage": (0, 240),
        "Current": (0, 50),
        "pH": (0, 14),
        "Vibration": (0, 100)
    }
    
    # Generate sensor IDs
    sensor_ids = [f"SENSOR-{random.randint(100, 999)}" for _ in range(50)]
    
    # Start date for time series
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(num_records):
        # Pick a sensor
        sensor_type = random.choice(sensor_types)
        sensor_id = random.choice(sensor_ids)
        location = random.choice(locations)
        
        # Generate a timestamp within the last 30 days
        time_offset = timedelta(
            days=random.randint(0, 29),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59)
        )
        timestamp = start_date + time_offset
        
        # Generate value based on sensor type
        value_range = value_ranges[sensor_type]
        if sensor_type == "Motion":
            value = random.randint(0, 1)  # Binary sensor
        else:
            value = round(random.uniform(value_range[0], value_range[1]), 2)
        
        # Generate a reading
        reading = {
            "id": str(uuid.uuid4()),
            "sensor_id": sensor_id,
            "sensor_type": sensor_type,
            "timestamp": timestamp.isoformat(),
            "value": value,
            "unit": units[sensor_type],
            "location": location,
            "status": "normal" if random.random() > 0.05 else random.choice(["warning", "error", "calibration"]),
            "battery_level": random.randint(0, 100) if random.random() > 0.3 else None
        }
        
        # Add some metadata for certain sensors
        if sensor_type in ["Temperature", "Humidity", "Pressure"]:
            reading["metadata"] = {
                "indoor": random.choice([True, False]),
                "floor": random.randint(1, 10) if reading["metadata"]["indoor"] else None,
                "latitude": round(random.uniform(30, 45), 6),
                "longitude": round(random.uniform(-120, -75), 6)
            }
        
        # Add to list
        readings.append(reading)
        
        # Show progress for large datasets
        if i > 0 and i % 10000 == 0:
            print(f"Generated {i} sensor readings...")
    
    print(f"Completed generating {len(readings)} sensor readings")
    return {
        "dataset_type": "sensor_data",
        "generated": datetime.now().isoformat(),
        "record_count": len(readings),
        "data": readings
    }

def generate_log_data(num_records):
    """Generate a large log dataset"""
    print(f"Generating log dataset with {num_records} records...")
    
    logs = []
    
    # Create some base data
    log_levels = ["INFO", "WARN", "ERROR", "DEBUG", "TRACE", "FATAL"]
    
    services = ["web-server", "api-gateway", "auth-service", "database", "cache", 
               "queue", "storage", "email-service", "payment-processor", "notification-service"]
    
    environments = ["production", "staging", "development", "testing"]
    
    # Standard HTTP status codes
    http_statuses = [200, 201, 204, 301, 302, 400, 401, 403, 404, 500, 502, 503]
    
    # Common error messages
    error_templates = [
        "Failed to connect to {service}",
        "Timeout waiting for response from {service}",
        "Database query failed: {error}",
        "Invalid input: {error}",
        "Authentication failed for user {user}",
        "Rate limit exceeded for IP {ip}",
        "Out of memory",
        "File not found: {path}",
        "Permission denied for {resource}",
        "Uncaught exception: {error}"
    ]
    
    # Start date for logs
    start_date = datetime.now() - timedelta(days=7)
    
    for i in range(num_records):
        # Pick service and environment
        service = random.choice(services)
        environment = random.choice(environments)
        
        # Generate a timestamp within the last 7 days
        time_offset = timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
            microseconds=random.randint(0, 999999)
        )
        timestamp = start_date + time_offset
        
        # Determine log level (weighting towards INFO)
        level_weights = [0.7, 0.15, 0.1, 0.03, 0.015, 0.005]
        log_level = random.choices(log_levels, weights=level_weights, k=1)[0]
        
        # Generate a log entry
        log = {
            "id": str(uuid.uuid4()),
            "timestamp": timestamp.isoformat(),
            "level": log_level,
            "service": service,
            "environment": environment,
            "host": f"{service}-{random.randint(1, 5)}.{environment}.example.com",
            "process_id": random.randint(1000, 9999),
            "thread_id": f"thread-{random.randint(1, 100)}",
            "trace_id": f"trace-{uuid.uuid4()}"
        }
        
        # Add message and details based on log level
        if log_level in ["INFO", "DEBUG", "TRACE"]:
            # Normal operation logs
            operations = [
                f"Request processed in {random.randint(5, 2000)}ms",
                f"User {random_string(8)} logged in",
                f"Cache hit ratio: {round(random.uniform(0.5, 1.0), 2)}",
                f"Processing batch job {random_string(8)}",
                f"Scheduled task completed: {random_string(10)}",
                f"Request received: {random.choice(['GET', 'POST', 'PUT', 'DELETE'])} /api/{random_string(8)}",
                f"Database connection established"
            ]
            log["message"] = random.choice(operations)
            
            # Add HTTP details for web requests
            if "Request" in log["message"]:
                log["http"] = {
                    "method": random.choice(["GET", "POST", "PUT", "DELETE", "PATCH"]),
                    "path": f"/api/{random.choice(['users', 'products', 'orders', 'payments', 'reports'])}/{random.randint(1, 9999)}",
                    "status": random.choice(http_statuses),
                    "user_agent": f"Mozilla/5.0 ({random.choice(['Windows', 'Mac', 'Linux', 'iOS', 'Android'])})",
                    "ip": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                    "duration_ms": random.randint(5, 5000)
                }
        else:
            # Error logs
            error_template = random.choice(error_templates)
            error_message = error_template.format(
                service=random.choice(services),
                error=random.choice([
                    "connection refused", 
                    "null pointer exception", 
                    "division by zero", 
                    "invalid argument",
                    "timeout",
                    "resource exhausted"
                ]),
                user=f"user-{random.randint(1000, 9999)}",
                ip=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                path=f"/path/to/file-{random.randint(1, 999)}.txt",
                resource=f"resource-{random.randint(1, 999)}"
            )
            log["message"] = error_message
            
            # Add stack trace for errors
            if log_level in ["ERROR", "FATAL"]:
                log["stacktrace"] = [
                    f"at com.example.{service}.{random_string(10)}.{random_string(8)}({random_string(8)}.java:{random.randint(10, 999)})",
                    f"at com.example.{service}.{random_string(10)}.{random_string(8)}({random_string(8)}.java:{random.randint(10, 999)})",
                    f"at com.example.common.{random_string(10)}.{random_string(8)}({random_string(8)}.java:{random.randint(10, 999)})"
                ]
        
        # Add to list
        logs.append(log)
        
        # Show progress for large datasets
        if i > 0 and i % 10000 == 0:
            print(f"Generated {i} log entries...")
    
    print(f"Completed generating {len(logs)} log entries")
    return {
        "dataset_type": "log_data",
        "generated": datetime.now().isoformat(),
        "record_count": len(logs),
        "data": logs
    }

def main():
    """Generate large JSON files for testing"""
    print(f"Generating {NUM_FILES} large JSON files in {JSON_FILES_DIR}")
    
    # Dataset generator functions
    generators = [
        generate_customer_data,
        generate_product_catalog,
        generate_transaction_data,
        generate_sensor_data,
        generate_log_data
    ]
    
    for i in range(NUM_FILES):
        # Choose a generator
        generator = generators[i % len(generators)]
        
        # Determine number of records
        num_records = random.randint(MIN_RECORDS_PER_FILE, MAX_RECORDS_PER_FILE)
        
        # Generate the data
        data = generator(num_records)
        
        # Determine filename based on data type
        filename = f"large_{data['dataset_type']}_{data['record_count']}_records.json"
        file_path = os.path.join(JSON_FILES_DIR, filename)
        
        # Save to file
        print(f"Saving to {file_path}...")
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
        # Calculate file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"Created {filename} - {file_size_mb:.2f} MB with {data['record_count']} records")
    
    print("\nSuccessfully generated large JSON test files!")

if __name__ == "__main__":
    main() 