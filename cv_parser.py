import re

def extract_name(cv_text):
    # Basitçe baştaki satırda isim aranabilir
    lines = cv_text.strip().split("\n")
    # İlk satırda genellikle isim olur
    return lines[0].strip()

def extract_email(cv_text):
    email_pattern = r'[\w\.-]+@[\w\.-]+'
    emails = re.findall(email_pattern, cv_text)
    return emails[0] if emails else None

def extract_phone(cv_text):
    phone_pattern = r'\+?\d[\d\s\-]{7,}\d'
    phones = re.findall(phone_pattern, cv_text)
    return phones[0] if phones else None
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