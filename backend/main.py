from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import pandas as pd
import numpy as np
from scipy import stats
import io
from datetime import datetime
import json

from app.database import get_db, init_db, engine
from app import models
from app.services import analysis, geo_service, cbioportal_service, ai_service, export_service

# Initialize database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SynOmix V5",
    description="Multi-Omics Integration Platform",
    version="5.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files - serve assets directly at root for Vite build
if os.path.exists("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ============ EXPERIMENT ENDPOINTS ============

@app.post("/api/experiment/create")
async def create_experiment(
    name: str = Form(...),
    cancer_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new experiment"""
    experiment = models.Experiment(
        name=name,
        cancer_type=cancer_type,
        user_id="default"  # TODO: Add auth
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    return {
        "id": experiment.id,
        "name": experiment.name,
        "cancer_type": experiment.cancer_type,
        "created_at": experiment.created_at.isoformat(),
        "updated_at": experiment.updated_at.isoformat(),
        "is_public": experiment.is_public,
    }

@app.get("/api/experiments")
async def get_experiments(db: Session = Depends(get_db)):
    """Get all experiments"""
    experiments = db.query(models.Experiment).all()
    return [
        {
            "id": exp.id,
            "name": exp.name,
            "cancer_type": exp.cancer_type,
            "created_at": exp.created_at.isoformat(),
            "status": exp.status,
        }
        for exp in experiments
    ]

@app.get("/api/experiment/{exp_id}")
async def get_experiment(exp_id: str, db: Session = Depends(get_db)):
    """Get single experiment"""
    experiment = db.query(models.Experiment).filter(models.Experiment.id == exp_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    return {
        "id": experiment.id,
        "name": experiment.name,
        "cancer_type": experiment.cancer_type,
        "created_at": experiment.created_at.isoformat(),
        "status": experiment.status,
        "is_public": experiment.is_public,
    }

@app.post("/api/experiment/{exp_id}/share")
async def share_experiment(exp_id: str, db: Session = Depends(get_db)):
    """Generate shareable link"""
    import secrets

    experiment = db.query(models.Experiment).filter(models.Experiment.id == exp_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    if not experiment.share_token:
        experiment.share_token = secrets.token_urlsafe(32)
        experiment.is_public = True
        db.commit()

    return {"share_url": f"/shared/{experiment.share_token}"}

# ============ FILE UPLOAD ============

@app.post("/api/experiment/{exp_id}/upload")
async def upload_file(
    exp_id: str,
    file: UploadFile = File(...),
    layer_type: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Upload and process omics data file"""
    experiment = db.query(models.Experiment).filter(models.Experiment.id == exp_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Read file
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', index_col=0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    # Auto-detect layer type if not provided
    if not layer_type:
        layer_type = analysis.detect_layer_type(file.filename)

    # Store layer info
    layer = models.Layer(
        experiment_id=exp_id,
        layer_type=layer_type,
        file_name=file.filename,
        gene_count=len(df.index),
        sample_count=len(df.columns),
        data_summary={
            "genes": df.index.tolist()[:100],  # Store first 100 genes
            "samples": df.columns.tolist(),
            "shape": df.shape
        }
    )
    db.add(layer)
    db.commit()

    return {
        "layer_type": layer_type,
        "gene_count": len(df.index),
        "sample_count": len(df.columns),
    }

# ============ ANALYSIS ============

@app.post("/api/experiment/{exp_id}/analyze")
async def analyze_experiment(exp_id: str, db: Session = Depends(get_db)):
    """Run multi-omics analysis"""
    experiment = db.query(models.Experiment).filter(models.Experiment.id == exp_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    experiment.status = "processing"
    db.commit()

    try:
        # Get all layers (simplified - in production, load actual data)
        layers = db.query(models.Layer).filter(models.Layer.experiment_id == exp_id).all()

        # Mock analysis results for now
        results = analysis.integrate_multi_omics({
            "layers": layers,
            "cancer_type": experiment.cancer_type
        })

        # Store results
        result = models.AnalysisResult(
            experiment_id=exp_id,
            layers_count=len(layers),
            novel_genes_count=results.get("novel_genes_count", 0),
            known_alterations_count=results.get("known_alterations_count", 0),
            multi_omics_hits=results.get("multi_omics_hits", 0),
            pathways_count=results.get("pathways_count", 0),
            hypotheses_count=results.get("hypotheses_count", 0),
            novel_findings=results.get("novel_findings", []),
            known_genes=results.get("known_genes", []),
            pathways=results.get("pathways", []),
            subtype_prediction=results.get("subtype_prediction"),
            hypotheses=results.get("hypotheses", []),
            narrative=results.get("narrative", "")
        )
        db.add(result)

        experiment.status = "completed"
        db.commit()

        return {"status": "success", "experiment_id": exp_id}

    except Exception as e:
        experiment.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

# ============ GEO INTEGRATION ============

@app.get("/api/geo/search")
async def search_geo(query: str, organism: Optional[str] = None):
    """Search GEO datasets"""
    return geo_service.search_datasets(query, organism)

@app.post("/api/geo/import/{accession}")
async def import_geo(accession: str, experiment_id: str, db: Session = Depends(get_db)):
    """Import data from GEO"""
    data = geo_service.fetch_dataset(accession)
    # Process and store
    return {"status": "success"}

# ============ CBIOPORTAL INTEGRATION ============

@app.get("/api/cbioportal/studies")
async def search_cbioportal(cancer_type: str):
    """Search cBioPortal studies"""
    return cbioportal_service.search_studies(cancer_type)

@app.post("/api/cbioportal/import/{study_id}")
async def import_cbioportal(study_id: str, experiment_id: str, db: Session = Depends(get_db)):
    """Import data from cBioPortal"""
    data = cbioportal_service.fetch_study(study_id)
    return {"status": "success"}

# ============ AI CHAT ============

@app.post("/api/chat")
async def chat(
    experiment_id: str = Form(...),
    message: str = Form(...),
    history: str = Form("[]"),  # JSON string
    db: Session = Depends(get_db)
):
    """AI-powered chat about analysis"""
    experiment = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    # Get results context
    results = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.experiment_id == experiment_id
    ).first()

    # Generate response using LLM
    response = await ai_service.generate_response(
        message=message,
        context={
            "experiment": experiment,
            "results": results
        },
        history=json.loads(history)
    )

    # Store in history
    chat_msg_user = models.ChatHistory(
        experiment_id=experiment_id,
        role="user",
        content=message
    )
    chat_msg_assistant = models.ChatHistory(
        experiment_id=experiment_id,
        role="assistant",
        content=response
    )
    db.add_all([chat_msg_user, chat_msg_assistant])
    db.commit()

    return {"response": response}

# ============ SURVIVAL ANALYSIS ============

@app.post("/api/experiment/{exp_id}/survival")
async def survival_analysis(
    exp_id: str,
    survival_data: dict,
    db: Session = Depends(get_db)
):
    """Perform survival analysis"""
    from lifelines import KaplanMeierFitter
    import json

    # Extract survival data
    times = [s['time'] for s in survival_data['survival_data']]
    events = [s['event'] for s in survival_data['survival_data']]

    # Fit Kaplan-Meier
    kmf = KaplanMeierFitter()
    kmf.fit(times, events)

    # Store results
    results = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.experiment_id == exp_id
    ).first()

    if results:
        results.survival_data = {
            "timeline": kmf.survival_function_.index.tolist(),
            "survival_probability": kmf.survival_function_['KM_estimate'].tolist(),
            "median_survival": float(kmf.median_survival_time_)
        }
        db.commit()

    return {"status": "success"}

# ============ BATCH ANALYSIS ============

@app.post("/api/experiments/batch-analyze")
async def batch_analyze(experiment_ids: List[str], db: Session = Depends(get_db)):
    """Batch analyze multiple experiments"""
    results = []
    for exp_id in experiment_ids:
        result = await analyze_experiment(exp_id, db)
        results.append(result)
    return results

# ============ EXPORT ============

@app.get("/api/experiment/{exp_id}/export/pdf")
async def export_pdf(exp_id: str, db: Session = Depends(get_db)):
    """Export results as PDF"""
    experiment = db.query(models.Experiment).filter(models.Experiment.id == exp_id).first()
    results = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.experiment_id == exp_id
    ).first()

    pdf_bytes = export_service.generate_pdf(experiment, results)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=synomix-{exp_id}.pdf"}
    )

@app.get("/api/experiment/{exp_id}/export/figure")
async def export_figure(
    exp_id: str,
    figure_type: str,
    format: str = "png",
    db: Session = Depends(get_db)
):
    """Export figure"""
    # Generate figure based on type
    return {"status": "success"}

# ============ TEAMS ============

@app.post("/api/teams")
async def create_team(name: str, description: str, db: Session = Depends(get_db)):
    """Create a team"""
    team = models.Team(name=name, description=description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return {"id": team.id, "name": team.name}

@app.get("/api/teams")
async def get_teams(db: Session = Depends(get_db)):
    """Get all teams"""
    teams = db.query(models.Team).all()
    return [{"id": t.id, "name": t.name, "description": t.description, "members": []} for t in teams]

@app.post("/api/teams/{team_id}/members")
async def add_team_member(team_id: str, email: str, role: str, db: Session = Depends(get_db)):
    """Add member to team"""
    # TODO: Implement user lookup and invitation
    return {"status": "success"}

# ============ SETTINGS ============

@app.get("/api/settings")
async def get_settings(db: Session = Depends(get_db)):
    """Get user settings"""
    # TODO: Add auth and get current user
    return {
        "theme": "dark",
        "notifications": True,
        "api_keys": {}
    }

@app.put("/api/settings")
async def update_settings(settings: dict, db: Session = Depends(get_db)):
    """Update user settings"""
    # TODO: Add auth and update current user
    return settings

# ============ SERVE FRONTEND ============

@app.get("/")
async def serve_frontend():
    """Serve frontend"""
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "SynOmix V5 API", "version": "5.0.0"}

@app.get("/api")
async def api_info():
    """API information"""
    return {"version": "5.0.0", "name": "SynOmix V5"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
