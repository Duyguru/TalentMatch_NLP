import spacy
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from transformers import pipeline

# spaCy modelini yükle
nlp = spacy.load("en_core_web_lg")

@dataclass
class CVInfo:
    name: str  # Ad-soyad
    email: str  # E-posta
    phone: Optional[str]  # Telefon
    education: List[Dict]  # Eğitim bilgileri
    experience: List[Dict]  # İş deneyimi
    skills: List[str]  # Beceriler
    summary: str  # Özet

def extract_name(text: str) -> str:
    """spaCy NER kullanarak CV'den isim çıkarma"""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_email(text: str) -> str:
    """Regex kullanarak e-posta çıkarma"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> Optional[str]:
    """Regex kullanarak telefon numarası çıkarma"""
    phone_pattern = r'\+?[\d\s-]{10,}'
    match = re.search(phone_pattern, text)
    return match.group(0) if match else None

def extract_education(text: str) -> List[Dict]:
    """spaCy ve regex kullanarak eğitim bilgilerini çıkarma"""
    education = []
    # Eğitim bölümünü bul
    edu_pattern = r'(?i)(education|academic|university|college|eğitim|üniversite).*?(?=\n\n|\Z)'
    edu_section = re.search(edu_pattern, text, re.DOTALL)
    
    if edu_section:
        doc = nlp(edu_section.group(0))
        # Tarihleri ve kurumları çıkar
        for ent in doc.ents:
            if ent.label_ in ["ORG", "DATE"]:
                education.append({
                    "institution": ent.text if ent.label_ == "ORG" else "",
                    "date": ent.text if ent.label_ == "DATE" else ""
                })
    
    return education

def extract_experience(text: str) -> List[Dict]:
    """spaCy ve regex kullanarak iş deneyimini çıkarma"""
    experience = []
    # Deneyim bölümünü bul
    exp_pattern = r'(?i)(experience|work|employment|deneyim|iş).*?(?=\n\n|\Z)'
    exp_section = re.search(exp_pattern, text, re.DOTALL)
    
    if exp_section:
        doc = nlp(exp_section.group(0))
        # Şirketleri, tarihleri ve pozisyonları çıkar
        current_exp = {}
        for ent in doc.ents:
            if ent.label_ == "ORG":
                if current_exp:
                    experience.append(current_exp)
                current_exp = {"company": ent.text}
            elif ent.label_ == "DATE":
                current_exp["date"] = ent.text
            elif ent.label_ == "WORK_OF_ART":
                current_exp["position"] = ent.text
        
        if current_exp:
            experience.append(current_exp)
    
    return experience

def extract_skills(text: str) -> List[str]:
    """spaCy ve önceden tanımlanmış beceri kalıpları kullanarak becerileri çıkarma"""
    skills = []
    # Yaygın teknik beceri kalıpları
    skill_patterns = [
        r'(?i)(python|java|javascript|react|node\.js|docker|kubernetes|aws|azure|gcp)',
        r'(?i)(machine learning|ai|artificial intelligence|data science|big data|yapay zeka|veri bilimi)',
        r'(?i)(sql|nosql|mongodb|postgresql|mysql)',
        r'(?i)(agile|scrum|devops|ci/cd)'
    ]
    
    for pattern in skill_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            skills.append(match.group(0).lower())
    
    return list(set(skills))

def generate_summary(text: str) -> str:
    """Transformers kullanarak özet çıkarma"""
    summarizer = pipeline("summarization")
    # Metni çok uzunsa parçalara böl
    max_chunk_length = 1024
    chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
    
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    return " ".join(summaries)

def parse_cv(text: str) -> CVInfo:
    """CV'yi ayrıştırıp tüm bilgileri çıkaran ana fonksiyon"""
    return CVInfo(
        name=extract_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        education=extract_education(text),
        experience=extract_experience(text),
        skills=extract_skills(text),
        summary=generate_summary(text)
    )

if __name__ == "__main__":
    example_cv = """
    Duygu Er
    duygu.er@example.com
    +90 555 123 4567
    
    Eğitim:
    Pamukkale Üniversitesi, Bilgisayar Mühendisliği, 3. sınıf
    
    Tecrübe:
    Stajyer, XYZ Şirketi, 2024
    
    Beceriler:
    Python, NLP, Machine Learning
    """
    print("İsim:", extract_name(example_cv))
    print("Email:", extract_email(example_cv))
    print("Telefon:", extract_phone(example_cv))