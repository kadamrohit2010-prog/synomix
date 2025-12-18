# SynOmix AI - Deployment Package

Multi-omics biological discovery platform with AI-powered insights.

## 🚀 Quick Deploy to Railway (Recommended)

### Step 1: Create Railway Account
Go to [railway.app](https://railway.app) and sign up with GitHub.

### Step 2: Deploy
1. Click "New Project" → "Deploy from GitHub repo"
2. Connect your GitHub and create a new repo
3. Upload these files to the repo
4. Railway will auto-detect and deploy

### Step 3: Get Your URL
Once deployed, you'll get a URL like: `synomix-production.up.railway.app`

---

## 🔧 Alternative: Deploy to Render.com

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect repo or upload files
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🖥️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Or with uvicorn
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000

---

## 📁 Files

```
SynOmix_Deploy/
├── main.py           # FastAPI backend + API
├── requirements.txt  # Python dependencies
├── Procfile          # For Heroku/Railway
├── railway.json      # Railway config
└── static/
    └── index.html    # Frontend UI
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/experiment/create` | POST | Create new experiment |
| `/api/experiment/{id}/upload` | POST | Upload omics layer |
| `/api/experiment/{id}/analyze` | POST | Run analysis |
| `/api/experiments` | GET | List experiments |
| `/api/quick` | POST | Quick single-file analysis |

API docs available at `/docs` when running.

---

## 📊 Supported File Formats

- Gene Expression: `.csv`, `.tsv`, `.cct`
- Mutations: `.vcf`, `.maf`, `.cbt`
- Methylation: `.csv`, `.cct`
- Copy Number: `.csv`, `.cct`
- All formats support `.gz` compression

---

## 🧬 Features

- Multi-layer omics integration
- Automatic file type detection
- Pathway enrichment analysis
- Cancer subtype prediction
- Drug target identification
- AI query interface

---

## 📧 Support

For issues or feedback: [your email]
