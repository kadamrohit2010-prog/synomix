#!/bin/bash

echo "🚀 SynOmix V5 Redeployment with Node.js 20"
echo "=========================================="

ssh root@104.248.78.16 << 'ENDSSH'
set -e

echo "✓ Connected to server!"

# Update Node.js to v20
echo "📦 Updating Node.js to v20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

echo "✓ Node.js version:"
node --version

# Update repository
echo "📥 Pulling latest changes..."
cd /root/synomix
git fetch origin
git checkout v5-features
git pull origin v5-features

# Build frontend with fixes
echo "🎨 Building frontend with TypeScript fixes..."
cd /root/synomix/frontend
npm install
npm run build

# Redeploy
echo "🐳 Redeploying services..."
cd /root/synomix
docker-compose down
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 15

echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🔍 Testing API..."
curl -s http://localhost:8000/api || echo "API not responding yet, give it a moment..."

echo ""
echo "✅ Redeployment complete!"
echo "🌐 Access your app at: http://www.synomix.ai"

ENDSSH

echo ""
echo "🎉 All done!"
