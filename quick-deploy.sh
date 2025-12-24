#!/bin/bash

# Quick Deployment Script for SynOmix V5
# This script will SSH to the server and deploy everything

echo "🚀 SynOmix V5 Quick Deploy"
echo "=========================="
echo ""
echo "Connecting to server: 104.248.78.16"
echo "You will be prompted for the password: synOmixRPK26G"
echo ""

ssh root@104.248.78.16 << 'ENDSSH'
set -e

echo "✓ Connected to server!"
echo ""

# Update system
echo "📦 Updating system..."
apt update -qq

# Install dependencies
echo "📦 Installing dependencies..."
apt install -y git docker.io docker-compose postgresql postgresql-contrib nginx certbot python3-certbot-nginx nodejs npm > /dev/null 2>&1

# Start Docker
systemctl start docker
systemctl enable docker

# Setup PostgreSQL
echo "🗄️  Setting up PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE synomix_v5;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER synomix WITH PASSWORD 'synomix_secure_2024';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE synomix_v5 TO synomix;" 2>/dev/null || true

# Clone/update repository
echo "📥 Cloning/updating repository..."
cd /root
if [ -d "synomix" ]; then
  cd synomix
  git fetch origin
  git checkout v5-features
  git pull origin v5-features
else
  git clone https://github.com/kadamrohit2010-prog/synomix.git
  cd synomix
  git checkout v5-features
fi

# Configure environment
echo "⚙️  Configuring environment..."
cd /root/synomix/backend
cp .env.example .env
sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://synomix:synomix_secure_2024@postgres:5432/synomix_v5|' .env

# Build frontend
echo "🎨 Building frontend..."
cd /root/synomix/frontend
npm install
npm run build

# Deploy with Docker
echo "🐳 Deploying with Docker..."
cd /root/synomix
docker-compose down 2>/dev/null || true
docker-compose up -d --build

# Configure Nginx
echo "🌐 Configuring Nginx..."
cat > /etc/nginx/sites-available/synomix << 'EOF'
server {
    listen 80;
    server_name www.synomix.ai synomix.ai;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/synomix /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Waiting for services to start..."
sleep 10

echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔍 Testing API..."
curl -s http://localhost:8000/api | head -n 5

echo ""
echo "✅ Deployment successful!"
echo "🌐 Access your app at: http://www.synomix.ai"
echo ""
echo "Note: To enable HTTPS, run on the server:"
echo "  certbot --nginx -d www.synomix.ai -d synomix.ai"

ENDSSH

echo ""
echo "🎉 All done! Check https://www.synomix.ai"
