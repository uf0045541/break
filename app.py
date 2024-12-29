from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# Load environment variables
app.config['ENV'] = os.getenv('FLASK_ENV', 'development')  # Default to 'development'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///customer_data.db')

@app.route('/')
def index():
    return f"Environment: {app.config['ENV']}, Database: {DATABASE_URL}"

# Directory to save customer data
DATA_DIR = 'customer_data'
os.makedirs(DATA_DIR, exist_ok=True)

def load_customers():
    """Load all customers from files."""
    customers = []
    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith('.json'):
            with open(os.path.join(DATA_DIR, file_name), 'r') as file:
                customers.append(json.load(file))
    return customers

def save_customer_to_file(customer):
    """Save a single customer to a file."""
    file_path = os.path.join(DATA_DIR, f"{customer['id']}.json")
    with open(file_path, 'w') as file:
        json.dump(customer, file)

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = load_customers()
    return jsonify(customers)

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.json

    if not data.get("photos") or not isinstance(data["photos"], list):
        return jsonify({"error": "Photos array is missing or invalid"}), 400

    customer_id = len(load_customers()) + 1
    customer = {
        "id": customer_id,
        "name": data.get("name"),
        "number": data.get("number"),
        "Carname": data.get("Carname"),
        "license_plate": data.get("license_plate"),
        "photos": data.get("photos"),  # Save the array of Base64 strings
        "date": data.get("date", "")
    }
    save_customer_to_file(customer)
    return jsonify({"message": "Customer added successfully", "customer": customer}), 201


@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    file_path = os.path.join(DATA_DIR, f"{customer_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": "Customer deleted successfully"})
    return jsonify({"message": "Customer not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
