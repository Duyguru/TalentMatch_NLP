from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uvicorn
from datetime import datetime

from document_processor import process_document
from cv_parser import parse_cv
from vector_matcher import VectorMatcher
from database import Database
from notifications import NotificationService
import os
from fastapi.encoders import jsonable_encoder


app = FastAPI(
    title="TalentMatch NLP API",
    description="Otomatik CV analizi ve aday eşleştirme için API",
    version="1.0.0"
)

# CORS middleware yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servisleri başlat
db = Database()
vector_matcher = VectorMatcher()
notification_service = NotificationService()

# Modeller
class JobPosting(BaseModel):
    title: str  # İş başlığı
    description: str  # İş açıklaması
    requirements: List[str]  # Gereksinimler
    location: str  # Konum
    company: str  # Şirket
    matching_parameters: Optional[dict] = None  # Eşleştirme parametreleri

class CandidateMatch(BaseModel):
    candidate_id: str  # Aday ID
    match_percentage: float  # Eşleşme yüzdesi
    missing_skills: List[str]  # Eksik beceriler
    explanation: str  # Açıklama

class MatchParameters(BaseModel):
    min_match_percentage: float = 70.0  # Minimum eşleşme yüzdesi
    required_skills: List[str] = []  # Gerekli beceriler
    preferred_skills: List[str] = []  # Tercih edilen beceriler

# Rotalar
@app.get("/")
async def root():
    return {"message": "TalentMatch NLP API'ye Hoş Geldiniz"}

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """
    CV dosyası yükleme ve işleme (PDF/DOCX)
    """
    if not file.filename.lower().endswith(('.pdf', '.docx')):
     raise HTTPException(status_code=400, detail="Sadece PDF ve DOCX dosyaları kabul edilir")

    try:
        # Dosya içeriğini oku
        file_content = await file.read()
        
        # Belgeyi işle
        
        ext = os.path.splitext(file.filename)[1]
        text = process_document(file_content, ext)
        
        # CV'yi ayrıştır
        cv_info = parse_cv(text)
        
        # Veritabanına kaydet
        cv_id = str(db.store_cv(cv_info.__dict__, file_content, file.filename))

        
        return {
         "message": "CV başarıyla yüklendi ve işlendi",
         "cv_id": cv_id,
         "parsed_info": jsonable_encoder(cv_info)
          }
    except Exception as e:
     import traceback
     traceback.print_exc()
     raise HTTPException(status_code=500, detail=str(e))

@app.post("/job-posting")
async def create_job_posting(job: JobPosting):
    """
    Yeni iş ilanı oluşturma
    """
    try:
        job_id = db.store_job_posting(job.dict())
        return {
            "message": "İş ilanı başarıyla oluşturuldu",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/match-candidates/{job_id}")
async def match_candidates(job_id: str):
    """
    Bir iş ilanı için uygun adayları bulma
    """
    try:
        # İş ilanını al
        job = db.get_job_posting(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="İş ilanı bulunamadı")
        
        # Tüm adayları al
        candidates = db.get_all_candidates()
        
        # Vektör indeksi oluştur
        vector_matcher.create_index(candidates)
        
        # Eşleşmeleri bul
        matches = vector_matcher.find_matches(
            f"{job['title']} {job['description']} {' '.join(job['requirements'])}"
        )
        
        # Eşleşmeleri kaydet ve bildirimleri gönder
        for match in matches:
            match_id = db.store_match(job_id, match["candidate_id"], match)
            
            # Bildirim için aday bilgilerini al
            candidate = db.get_cv(match["candidate_id"])
            if candidate:
                notification_service.send_match_notification(
                    candidate.get("email"),
                    candidate.get("phone"),
                    match
                )
        
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/job-posting/{job_id}/parameters")
async def update_match_parameters(job_id: str, parameters: MatchParameters):
    """
    İş ilanı için eşleştirme parametrelerini güncelleme
    """
    try:
        success = db.update_match_parameters(job_id, parameters.dict())
        if not success:
            raise HTTPException(status_code=404, detail="İş ilanı bulunamadı")
        
        return {"message": "Eşleştirme parametreleri başarıyla güncellendi"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/job-posting/{job_id}/matches")
async def get_job_matches(job_id: str):
    """
    Bir iş ilanı için tüm eşleşmeleri alma
    """
    try:
        matches = db.get_matches_for_job(job_id)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
