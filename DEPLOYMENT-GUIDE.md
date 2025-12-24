# SynOmix V5 Production Deployment Guide

## Server Details
- **IP**: 104.248.78.16
- **User**: root
- **Domain**: www.synomix.ai
- **Password**: synOmixRPK26G

## Step-by-Step Deployment

### Step 1: Connect to Server
```bash
ssh root@104.248.78.16
# Password: synOmixRPK26G
```

### Step 2: Update System & Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
  git \
  docker.io \
  docker-compose \
  postgresql \
  postgresql-contrib \
  nginx \
  certbot \
  python3-certbot-nginx \
  nodejs \
  npm

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 3: Set Up PostgreSQL Database
```bash
# Switch to postgres user and create database
sudo -u postgres psql << 'EOF'
-- Create database
CREATE DATABASE synomix_v5;

-- Create user
CREATE USER synomix WITH PASSWORD 'synomix_secure_2024';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE synomix_v5 TO synomix;

-- Exit
\q
EOF

# Verify database creation
sudo -u postgres psql -l | grep synomix_v5
```

### Step 4: Clone Repository
```bash
# Navigate to root directory
cd /root

# Clone if not exists, otherwise update
if [ -d "synomix" ]; then
  echo "Updating existing repository..."
  cd synomix
  git fetch origin
  git checkout v5-features
  git pull origin v5-features
else
  echo "Cloning repository..."
  git clone https://github.com/kadamrohit2010-prog/synomix.git
  cd synomix
  git checkout v5-features
fi
```

### Step 5: Configure Environment Variables
```bash
# Navigate to backend directory
cd /root/synomix/backend

# Copy example env file
cp .env.example .env

# Edit .env file with production values
nano .env
```

**Edit the .env file with these values:**
```bash
DATABASE_URL=postgresql://synomix:synomix_secure_2024@postgres:5432/synomix_v5
OPENAI_API_KEY=your_openai_key_here  # Add your key
ANTHROPIC_API_KEY=your_anthropic_key_here  # Add your key
SECRET_KEY=$(openssl rand -hex 32)
PORT=8000
```

Save with `CTRL+X`, `Y`, `Enter`

### Step 6: Build Frontend
```bash
# Navigate to frontend directory
cd /root/synomix/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Verify build
ls -la ../backend/static/
```

### Step 7: Deploy with Docker Compose
```bash
# Navigate to project root
cd /root/synomix

# Stop any existing containers
docker-compose down

# Build and start services
docker-compose up -d --build

# Wait for services to start (about 30 seconds)
sleep 30

# Check status
docker-compose ps

# Check logs
docker-compose logs -f --tail=50
```

### Step 8: Configure Nginx as Reverse Proxy
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/synomix > /dev/null << 'EOF'
server {
    listen 80;
    server_name www.synomix.ai synomix.ai;

    # Increase timeouts for long-running analyses
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';

        # Standard headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_cache_bypass $http_upgrade;
    }

    # Health check endpoint
    location /api {
        proxy_pass http://localhost:8000/api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/synomix /etc/nginx/sites-enabled/

# Remove default site if exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 9: Set Up SSL Certificate (HTTPS)
```bash
# Install SSL certificate with Let's Encrypt
sudo certbot --nginx \
  -d www.synomix.ai \
  -d synomix.ai \
  --non-interactive \
  --agree-tos \
  -m your-email@example.com

# Test auto-renewal
sudo certbot renew --dry-run

# Set up auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Step 10: Verify Deployment
```bash
# Check if containers are running
docker-compose ps

# Check backend API
curl http://localhost:8000/api

# Check frontend
curl http://localhost:8000/

# Check external access
curl http://www.synomix.ai/api

# Check HTTPS
curl https://www.synomix.ai/api

# View logs
docker-compose logs backend --tail=100
```

## Troubleshooting

### If containers fail to start:
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose up -d --build
```

### If PostgreSQL connection fails:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test database connection
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

### If Nginx fails:
```bash
# Check Nginx status
sudo systemctl status nginx

# Check configuration
sudo nginx -t

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
```

### If frontend doesn't load:
```bash
# Check if static files exist
ls -la /root/synomix/backend/static/

# Rebuild frontend
cd /root/synomix/frontend
npm run build

# Restart backend
cd /root/synomix
docker-compose restart backend
```

## Maintenance Commands

### View logs:
```bash
cd /root/synomix
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart services:
```bash
cd /root/synomix
docker-compose restart
```

### Update to latest code:
```bash
cd /root/synomix
git pull origin v5-features
cd frontend && npm install && npm run build && cd ..
docker-compose down
docker-compose up -d --build
```

### Backup database:
```bash
docker-compose exec postgres pg_dump -U synomix synomix_v5 > backup_$(date +%Y%m%d).sql
```

### Monitor system resources:
```bash
# CPU and memory usage
docker stats

# Disk usage
df -h
```

## Final Verification Checklist

- [ ] PostgreSQL database created and accessible
- [ ] Repository cloned and on v5-features branch
- [ ] Environment variables configured
- [ ] Frontend built successfully
- [ ] Docker containers running (postgres and backend)
- [ ] Nginx configured and running
- [ ] SSL certificate installed
- [ ] API responding at http://localhost:8000/api
- [ ] Website accessible at https://www.synomix.ai
- [ ] Frontend loads correctly
- [ ] Can create experiments and upload files

## Support

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Verify all services are running: `docker-compose ps`
3. Check Nginx: `sudo systemctl status nginx`
4. Test database connection
5. Review environment variables in backend/.env

---

**Deployment completed!** 🎉

Access your application at: **https://www.synomix.ai**
