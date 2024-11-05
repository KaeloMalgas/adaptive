#!/bin/bash

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
sudo apt-get install -y python3-pip python3-venv nginx

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set up Nginx
sudo cp nginx.conf /etc/nginx/sites-available/adaptive_testing
sudo ln -s /etc/nginx/sites-available/adaptive_testing /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Set up Gunicorn service
sudo cp gunicorn.service /etc/systemd/system/
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

echo "Deployment complete!"
