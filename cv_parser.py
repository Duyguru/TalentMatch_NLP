from langdetect import detect
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
    email = extract_email(text)
    if email:
        lines = text.splitlines()
        for i, line in enumerate(lines):
            if email in line:
                if i > 0:
                    name_candidate = lines[i - 1].strip()
                    if 2 <= len(name_candidate.split()) <= 4:  # örn: "Duygu Er"
                        return name_candidate
    # Fallback: spaCy
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and "dil" not in ent.text.lower():
            return ent.text
    return ""
def extract_email(text: str) -> str:
    text = text.replace("LANGUAGES", "").replace("Languages", "")

    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return emails[0] if emails else ""


def extract_phone(text: str) -> Optional[str]:
    phone_pattern = r'(\+90\s*\d{3}\s*\d{3}\s*\d{4})|(\d{10,11})'
    match = re.search(phone_pattern, text.replace('-', '').replace(' ', ''))
    return match.group(0) if match else None


def extract_education(text: str) -> List[Dict]:
    education = []
    lines = text.lower().split('\n')
    keywords = ["üniversite", "university", "fakülte", "bölüm", "yüksekokul", "yüksek lisans", "lisans", "lise"]
    
    for line in lines:
        if any(keyword in line for keyword in keywords):
            education.append({"institution": line.strip(), "date": ""})
    return education


def extract_experience(text: str) -> List[Dict]:
    experience = []
    lines = text.lower().split('\n')
    exp_keywords = ["staj", "çalıştı", "intern", "developer", "engineer", "mühendis", "şirket", "firm", "company"]
    
    for line in lines:
        if any(k in line for k in exp_keywords):
            experience.append({"company": line.strip()})
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
    if not isinstance(text, str):
        text = text.decode("utf-8", errors="ignore")

    if detect(text) != "en":
        return "Özetleme yalnızca İngilizce CV'ler için kullanılabilir."

    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
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