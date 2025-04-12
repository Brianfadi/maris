# Maris Logistics System

A comprehensive logistics management system built with Django.

## Deployment on Render.com

### Prerequisites
- A GitHub account
- A Render.com account

### Steps to Deploy

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push
   ```

2. **Create a Web Service on Render**
   - Go to [render.com](https://render.com) and sign in
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: Choose a name for your service
     - **Environment**: Python 3
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn logistics.wsgi:application`
     - **Plan**: Choose the Free plan (or any other plan you prefer)

3. **Add Environment Variables**
   - In the Render dashboard, go to your web service
   - Click on "Environment" tab
   - Add the following environment variables:
     ```
     DJANGO_SECRET_KEY=<your-secret-key>
     DJANGO_DEBUG=False
     PYTHON_VERSION=3.9.12
     ```

4. **Create a PostgreSQL Database (Optional but Recommended)**
   - In the Render dashboard, click "New +" and select "PostgreSQL"
   - Choose a name and plan
   - After creation, note the "Internal Database URL"
   - Add this URL as your `DATABASE_URL` environment variable in your web service settings

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application

### Troubleshooting

If you encounter any issues during deployment:

1. Check the build logs in the Render dashboard
2. Ensure all environment variables are set correctly
3. Make sure your `build.sh` file has execute permissions:
   ```bash
   git update-index --chmod=+x build.sh
   git add .
   git commit -m "Make build.sh executable"
   git push
   ```

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

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