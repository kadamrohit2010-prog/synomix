#!/usr/bin/expect -f

set timeout -1

# Server details
set server "root@104.248.78.16"
set password "synOmixRPK26G"

# Connect to server
spawn ssh $server

# Handle SSH password prompt
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "$ " {
        # We're in! Now run deployment commands
    }
}

# Update system
send "apt update && apt upgrade -y\r"
expect "$ "

# Install dependencies
send "apt install -y git docker.io docker-compose postgresql postgresql-contrib nginx certbot python3-certbot-nginx nodejs npm\r"
expect "$ "

# Set up PostgreSQL
send "sudo -u postgres psql -c \"CREATE DATABASE synomix_v5;\" || true\r"
expect "$ "
send "sudo -u postgres psql -c \"CREATE USER synomix WITH PASSWORD 'synomix_secure_2024';\" || true\r"
expect "$ "
send "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE synomix_v5 TO synomix;\" || true\r"
expect "$ "

# Clone/update repository
send "cd /root && if \[ -d synomix \]; then cd synomix && git fetch && git checkout v5-features && git pull; else git clone https://github.com/kadamrohit2010-prog/synomix.git && cd synomix && git checkout v5-features; fi\r"
expect "$ "

# Configure environment
send "cd /root/synomix && cp backend/.env.example backend/.env\r"
expect "$ "

# Update DATABASE_URL in .env
send "sed -i 's|DATABASE_URL=.*|DATABASE_URL=postgresql://synomix:synomix_secure_2024@localhost/synomix_v5|' backend/.env\r"
expect "$ "

# Build frontend
send "cd /root/synomix/frontend && npm install && npm run build\r"
expect "$ "

# Start services with Docker Compose
send "cd /root/synomix && docker-compose down && docker-compose up -d --build\r"
expect "$ "

# Configure Nginx
send "cat > /etc/nginx/sites-available/synomix << 'EOF'
server {
    listen 80;
    server_name www.synomix.ai synomix.ai;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF\r"
expect "$ "

send "ln -sf /etc/nginx/sites-available/synomix /etc/nginx/sites-enabled/ && nginx -t && systemctl restart nginx\r"
expect "$ "

# Verify deployment
send "docker-compose ps\r"
expect "$ "

send "curl http://localhost:8000/api\r"
expect "$ "

send "exit\r"
expect eof
