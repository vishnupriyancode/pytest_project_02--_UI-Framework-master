import os
import json
import random
from datetime import datetime, timedelta
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuration - set this to your application's expected input folder
JSON_FILES_DIR = r"C:\json_files"

# Ensure directory exists
os.makedirs(JSON_FILES_DIR, exist_ok=True)

def generate_sample_jsons(count=5):
    """Generate multiple sample JSON files with different structures"""
    print(f"Generating {count} sample JSON files in {JSON_FILES_DIR}")
    
    # Sample data templates
    templates = [
        # Template 1: Simple customer data
        {
            "customer_id": None,  # Will be filled
            "name": None,  # Will be filled
            "email": None,  # Will be filled
            "subscription": {
                "plan": None,  # Will be filled
                "active": True,
                "start_date": None  # Will be filled
            },
            "metadata": {
                "source": "sample_generator",
                "version": "1.0"
            }
        },
        
        # Template 2: Product data
        {
            "product_id": None,  # Will be filled
            "name": None,  # Will be filled
            "price": None,  # Will be filled
            "category": None,  # Will be filled
            "in_stock": True,
            "attributes": {
                "color": None,  # Will be filled
                "size": None,  # Will be filled
                "weight": None  # Will be filled
            },
            "tags": []  # Will be filled
        },
        
        # Template 3: Transaction data
        {
            "transaction_id": None,  # Will be filled
            "date": None,  # Will be filled
            "customer": {
                "id": None,  # Will be filled
                "name": None  # Will be filled
            },
            "items": [],  # Will be filled
            "payment": {
                "method": None,  # Will be filled
                "amount": None,  # Will be filled
                "currency": "USD",
                "status": "completed"
            }
        },
        
        # Template 4: User profile
        {
            "user_id": None,  # Will be filled
            "username": None,  # Will be filled
            "profile": {
                "first_name": None,  # Will be filled
                "last_name": None,  # Will be filled
                "age": None,  # Will be filled
                "location": {
                    "city": None,  # Will be filled
                    "country": None  # Will be filled
                }
            },
            "preferences": {
                "theme": "dark",
                "notifications": True,
                "language": "en"
            },
            "last_login": None  # Will be filled
        },
        
        # Template 5: Event data
        {
            "event_id": None,  # Will be filled
            "name": None,  # Will be filled
            "type": None,  # Will be filled
            "timestamp": None,  # Will be filled
            "source": "application",
            "data": {
                "action": None,  # Will be filled
                "resource": None,  # Will be filled
                "status": "success"
            },
            "metadata": {
                "version": "1.0",
                "environment": "test"
            }
        }
    ]
    
    # Sample data for filling in templates
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    products = ["Laptop", "Smartphone", "Headphones", "Tablet", "Monitor", "Keyboard", "Mouse", "Printer", "Camera", "Speaker"]
    categories = ["Electronics", "Clothing", "Home", "Books", "Sports", "Beauty", "Toys", "Food", "Automotive", "Garden"]
    colors = ["Red", "Blue", "Green", "Yellow", "Black", "White", "Purple", "Orange", "Pink", "Gray"]
    sizes = ["Small", "Medium", "Large", "XL", "XXL", "Tiny", "Huge", "Standard", "Compact", "Oversized"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    countries = ["USA", "Canada", "UK", "Germany", "France", "Australia", "Japan", "China", "Brazil", "India"]
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Apple Pay", "Google Pay", "Bitcoin", "Gift Card", "Cash", "Check", "Venmo"]
    event_types = ["Login", "Purchase", "Registration", "View", "Update", "Delete", "Download", "Upload", "Share", "Comment"]
    actions = ["Create", "Read", "Update", "Delete", "Modify", "View", "Process", "Analyze", "Export", "Import"]
    resources = ["User", "Product", "Order", "Invoice", "Payment", "Report", "Document", "Image", "Video", "Audio"]
    
    # Generate the sample JSON files
    generated_files = []
    
    for i in range(count):
        # Select a random template
        template = random.choice(templates).copy()
        template_type = templates.index(template) + 1
        
        # Fill in the template based on its type
        if template_type == 1:  # Customer data
            template["customer_id"] = f"CUST-{random.randint(10000, 99999)}"
            template["name"] = f"{random.choice(first_names)} {random.choice(last_names)}"
            template["email"] = f"{template['name'].lower().replace(' ', '.')}@example.com"
            template["subscription"]["plan"] = random.choice(["Basic", "Premium", "Pro", "Enterprise"])
            
            # Generate a start date in the past
            start_date = datetime.now() - timedelta(days=random.randint(1, 365))
            template["subscription"]["start_date"] = start_date.strftime("%Y-%m-%d")
            
        elif template_type == 2:  # Product data
            template["product_id"] = f"PROD-{random.randint(10000, 99999)}"
            template["name"] = random.choice(products)
            template["price"] = round(random.uniform(10.0, 1000.0), 2)
            template["category"] = random.choice(categories)
            template["attributes"]["color"] = random.choice(colors)
            template["attributes"]["size"] = random.choice(sizes)
            template["attributes"]["weight"] = round(random.uniform(0.1, 10.0), 1)
            template["tags"] = random.sample(["new", "sale", "featured", "limited", "bestseller", "eco-friendly"], random.randint(1, 3))
            
        elif template_type == 3:  # Transaction data
            template["transaction_id"] = f"TRX-{random.randint(100000, 999999)}"
            template["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            template["customer"]["id"] = f"CUST-{random.randint(10000, 99999)}"
            template["customer"]["name"] = f"{random.choice(first_names)} {random.choice(last_names)}"
            
            # Add items
            num_items = random.randint(1, 4)
            item_total = 0
            for j in range(num_items):
                price = round(random.uniform(10.0, 200.0), 2)
                quantity = random.randint(1, 5)
                item_total += price * quantity
                
                template["items"].append({
                    "id": f"ITEM-{random.randint(1000, 9999)}",
                    "name": random.choice(products),
                    "price": price,
                    "quantity": quantity,
                    "subtotal": round(price * quantity, 2)
                })
            
            template["payment"]["method"] = random.choice(payment_methods)
            template["payment"]["amount"] = round(item_total, 2)
            
        elif template_type == 4:  # User profile
            template["user_id"] = f"USER-{random.randint(10000, 99999)}"
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            template["username"] = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 99)}"
            template["profile"]["first_name"] = first_name
            template["profile"]["last_name"] = last_name
            template["profile"]["age"] = random.randint(18, 70)
            template["profile"]["location"]["city"] = random.choice(cities)
            template["profile"]["location"]["country"] = random.choice(countries)
            
            # Generate a last login time in the past
            last_login = datetime.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            template["last_login"] = last_login.strftime("%Y-%m-%d %H:%M:%S")
            
        elif template_type == 5:  # Event data
            template["event_id"] = f"EVT-{random.randint(100000, 999999)}"
            template["name"] = f"{random.choice(event_types)} event"
            template["type"] = random.choice(event_types)
            template["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            template["data"]["action"] = random.choice(actions)
            template["data"]["resource"] = random.choice(resources)
        
        # Determine filename based on template type
        filename = f"sample_{template_type}_{i+1}.json"
        file_path = os.path.join(JSON_FILES_DIR, filename)
        
        # Write to file
        with open(file_path, 'w') as f:
            json.dump(template, f, indent=2)
            
        generated_files.append(file_path)
        print(f"Generated: {file_path}")
    
    return generated_files

if __name__ == "__main__":
    # Generate sample JSON files
    num_files = 10
    files = generate_sample_jsons(num_files)
    print(f"\nSuccessfully generated {len(files)} sample JSON files in {JSON_FILES_DIR}")
    print("Run the application to process these files.")

# Create a semaphore to limit concurrent requests
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# Process files concurrently with semaphore
tasks = [
    self.process_file(file_path, semaphore)
    for file_path in json_files
]

# Wait for all tasks to complete
self.results = await asyncio.gather(*tasks)

# Store responses in database
db = get_db_connection(db_type='sqlite')  # or 'postgresql'
db.save_processing_results(results)

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_exponential(multiplier=RETRY_DELAY))
async def _send_api_request(self, data):
    """Send API request with retry logic"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                API_ENDPOINT, 
                json=data,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
            ) as response:
                # ... error handling and response processing 