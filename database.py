from pymongo import MongoClient
from gridfs import GridFS
from typing import Dict, List, Optional
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        """
        MongoDB bağlantısını ve GridFS'i başlat
        """
        self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
        self.db = self.client.talentmatch
        self.fs = GridFS(self.db)
        
        # Koleksiyonlar
        self.candidates = self.db.candidates
        self.job_postings = self.db.job_postings
        self.matches = self.db.matches
        
    def store_cv(self, cv_data: Dict, file_content: bytes, filename: str) -> str:
        """
        CV dosyasını GridFS'e ve meta verileri candidates koleksiyonuna kaydet
        """
        # Dosyayı GridFS'e kaydet
        file_id = self.fs.put(
            file_content,
            filename=filename,
            content_type="application/pdf" if filename.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Meta verileri kaydet
        cv_data["file_id"] = file_id
        cv_data["created_at"] = datetime.utcnow()
        result = self.candidates.insert_one(cv_data)
        
        return str(result.inserted_id)
    
    def get_cv(self, cv_id: str) -> Optional[Dict]:
        """
        CV meta verilerini ve dosya içeriğini al
        """
        cv_data = self.candidates.find_one({"_id": cv_id})
        if cv_data and "file_id" in cv_data:
            file_data = self.fs.get(cv_data["file_id"])
            cv_data["file_content"] = file_data.read()
            return cv_data
        return None
    
    def store_job_posting(self, job_data: Dict) -> str:
        """
        İş ilanını veritabanına kaydet
        """
        job_data["created_at"] = datetime.utcnow()
        result = self.job_postings.insert_one(job_data)
        return str(result.inserted_id)
    
    def get_job_posting(self, job_id: str) -> Optional[Dict]:
        """
        İş ilanını veritabanından al
        """
        return self.job_postings.find_one({"_id": job_id})
    
    def store_match(self, job_id: str, candidate_id: str, match_data: Dict) -> str:
        """
        Eşleşme sonucunu veritabanına kaydet
        """
        match_data.update({
            "job_id": job_id,
            "candidate_id": candidate_id,
            "created_at": datetime.utcnow()
        })
        result = self.matches.insert_one(match_data)
        return str(result.inserted_id)
    
    def get_matches_for_job(self, job_id: str) -> List[Dict]:
        """
        Bir iş ilanı için tüm eşleşmeleri al
        """
        return list(self.matches.find({"job_id": job_id}).sort("match_percentage", -1))
    
    def get_all_candidates(self) -> List[Dict]:
        """
        Tüm adayları al
        """
        return list(self.candidates.find())
    
    def get_all_job_postings(self) -> List[Dict]:
        """
        Tüm iş ilanlarını al
        """
        return list(self.job_postings.find())
    
    def update_match_parameters(self, job_id: str, parameters: Dict) -> bool:
        """
        İş ilanı için eşleştirme parametrelerini güncelle
        """
        result = self.job_postings.update_one(
            {"_id": job_id},
            {"$set": {"matching_parameters": parameters}}
        )
        return result.modified_count > 0 