from cv_parser import extract_name, extract_email, extract_phone

cv_text = """Buraya test CV metnini koyabilirsin"""

print("İsim:", extract_name(cv_text))
print("Email:", extract_email(cv_text))
print("Telefon:", extract_phone(cv_text))

from read_pdf import extract_text_from_pdf


cv_path = "cvler/DuyguCV.pdf"  
cv_text = extract_text_from_pdf(cv_path)

print("CV'den alınan metin:\n")
print(cv_text)
