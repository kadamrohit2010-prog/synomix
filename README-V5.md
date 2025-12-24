# SynOmix V5 - Multi-Omics Integration Platform

## 🚀 What's New in V5

### Frontend Enhancements
- ✨ **Animated Hero**: Eye-catching "60 Seconds" tagline with smooth animations
- 📤 **Drag & Drop Upload**: Intuitive file upload with progress tracking
- 📊 **Progress Stepper**: Visual workflow guidance through analysis steps
- 🔬 **Interactive Venn Diagram**: Visualize multi-omics overlaps
- 🕸️ **Pathway Network Graph**: Interactive D3-powered network visualization
- 🤖 **AI Chat Sidebar**: Real LLM-powered analysis assistant (OpenAI/Anthropic)
- 🔍 **Gene Detail Modal**: Comprehensive gene information with charts and external links

### New Pages
- 📚 **Data Browser**: Search and import from GEO and cBioPortal
- 👥 **Collaboration**: Team management and experiment sharing
- ⚙️ **Settings**: User preferences and API key management

### Backend Improvements
- 🗄️ **PostgreSQL Database**: Persistent storage for experiments and results
- 🔗 **GEO Integration**: Import gene expression data from NCBI GEO
- 🧬 **cBioPortal Integration**: Access cancer genomics studies
- 🧪 **Metabolomics Support**: Analyze metabolic profiling data
- 🔬 **Single-Cell RNA-seq**: Support for single-cell transcriptomics
- 📦 **Batch Analysis**: Process multiple experiments simultaneously
- 📈 **Survival Analysis**: Kaplan-Meier survival curves with lifelines
- 🤖 **Real LLM Integration**: OpenAI GPT-4 and Anthropic Claude support

### Enhanced Features
- 🔗 **Shareable Links**: Generate public links to share experiments
- 📄 **PDF Reports**: Download comprehensive analysis reports
- 🖼️ **Figure Export**: Export visualizations in multiple formats
- 👥 **Team Collaboration**: Share experiments with teams
- 🎨 **Modern UI**: Glassmorphic design with Tailwind CSS and Framer Motion

## 🏗️ Architecture

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS with custom glassmorphic components
- **Animation**: Framer Motion
- **Visualization**: D3.js, Recharts
- **Routing**: React Router
- **State**: React Hooks

### Backend
- **Framework**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **File Processing**: Pandas, NumPy, SciPy
- **Analysis**: Custom multi-omics integration algorithms
- **AI**: OpenAI API / Anthropic API
- **Bioinformatics**: Biopython, GEOparse, lifelines

## 📋 Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (for containerized deployment)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/kadamrohit2010-prog/synomix.git
cd synomix
git checkout v5-features
```

2. **Set up environment variables**
```bash
# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env and add your API keys
```

3. **Run deployment script**
```bash
chmod +x deploy.sh
./deploy.sh
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb synomix_v5

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run backend
python main.py
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Or build for production
npm run build
```

## 🗄️ Database Setup

### Local PostgreSQL

```bash
# Install PostgreSQL (if not already installed)
# macOS
brew install postgresql@16

# Ubuntu/Debian
sudo apt-get install postgresql-16

# Create database and user
psql postgres
CREATE DATABASE synomix_v5;
CREATE USER synomix WITH PASSWORD 'synomix';
GRANT ALL PRIVILEGES ON DATABASE synomix_v5 TO synomix;
\q
```

### Production (DigitalOcean)

```bash
# SSH to server
ssh root@104.248.78.16

# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Configure database
sudo -u postgres psql
CREATE DATABASE synomix_v5;
CREATE USER synomix WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE synomix_v5 TO synomix;
\q
```

## 🔑 API Keys Configuration

Edit `backend/.env`:

```bash
# OpenAI (for AI chat)
OPENAI_API_KEY=sk-...

# Or Anthropic Claude (alternative)
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://synomix:synomix@localhost/synomix_v5

# Security
SECRET_KEY=your-secret-key-here
```

## 🚢 Production Deployment

### Deploy to DigitalOcean Droplet

1. **Prepare server**
```bash
ssh root@104.248.78.16

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin
```

2. **Clone and deploy**
```bash
git clone https://github.com/kadamrohit2010-prog/synomix.git
cd synomix
git checkout v5-features

# Set up environment
cp backend/.env.example backend/.env
nano backend/.env  # Edit with production values

# Deploy
chmod +x deploy.sh
./deploy.sh
```

3. **Configure Nginx (reverse proxy)**
```bash
sudo apt install nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/synomix

# Add configuration:
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
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/synomix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Set up SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d www.synomix.ai -d synomix.ai
```

## 📦 Project Structure

```
synomix-v4-real/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   │   ├── ui/         # UI components
│   │   │   └── visualizations/  # Charts & graphs
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx         # Main app component
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── database.py     # Database configuration
│   │   └── services/       # Business logic
│   │       ├── analysis.py
│   │       ├── geo_service.py
│   │       ├── cbioportal_service.py
│   │       ├── ai_service.py
│   │       └── export_service.py
│   ├── main.py             # FastAPI application
│   └── requirements.txt
│
├── Dockerfile
├── docker-compose.yml
├── deploy.sh
└── README-V5.md
```

## 🧪 Development

### Run tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code formatting
```bash
# Backend
black app/
isort app/

# Frontend
npm run lint
npm run format
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- NCBI GEO for genomics data
- cBioPortal for cancer genomics
- OpenAI and Anthropic for AI capabilities
- Open source bioinformatics community

## 📞 Support

- Issues: https://github.com/kadamrohit2010-prog/synomix/issues
- Email: support@synomix.ai
- Website: https://www.synomix.ai

---

**SynOmix V5** - From Multi-Omics Data to Breakthrough Insights in 60 Seconds ⚡
