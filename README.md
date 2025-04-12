# Logistics Management System

A comprehensive logistics management system built with Django, similar to Maris Logistics.

## Features

- User Authentication and Authorization
- Shipment Tracking
- Freight Management
- Warehouse Management
- Customer Portal
- Admin Dashboard
- Real-time Shipment Status Updates
- Document Management
- Route Optimization
- Cost Management

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory with:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `logistics/` - Main project directory
- `accounts/` - User authentication and management
- `shipments/` - Shipment tracking and management
- `warehouse/` - Warehouse operations
- `customers/` - Customer portal
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 