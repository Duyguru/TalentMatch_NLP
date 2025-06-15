# TalentMatch NLP

TalentMatch NLP, doğal dil işleme kullanarak iş arayanları iş ilanlarıyla eşleştiren otomatik CV analiz ve aday eşleştirme sistemidir.

## Özellikler

- PDF/DOCX CV ayrıştırma ve bilgi çıkarma
- Otomatik beceri ve deneyim eşleştirme
- FAISS kullanarak vektör tabanlı benzerlik arama
- Eşleşmeler için e-posta ve SMS bildirimleri
- Diğer sistemlerle entegrasyon için RESTful API
- GDPR uyumlu veri depolama
- CV'lerin özet çıkarımı

## Gereksinimler

- Python 3.8+
- MongoDB
- E-posta bildirimleri için SMTP sunucusu
- SMS bildirimleri için Twilio hesabı (isteğe bağlı)

## Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/yourusername/TalentMatch_NLP.git
cd TalentMatch_NLP
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. spaCy modelini indirin:
```bash
python -m spacy download en_core_web_lg
```

5. Aşağıdaki değişkenleri içeren bir `.env` dosyası oluşturun:
```env
MONGODB_URI=mongodb://localhost:27017/
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-phone
```

## Kullanım

1. FastAPI sunucusunu başlatın:
```bash
uvicorn main:app --reload
```

2. API dokümantasyonuna `http://localhost:8000/docs` adresinden erişin

## API Uç Noktaları

### CV Yönetimi

- `POST /upload-cv`: CV dosyası yükleme ve işleme
- `GET /cv/{cv_id}`: CV bilgilerini alma

### İş İlanları

- `POST /job-posting`: Yeni iş ilanı oluşturma
- `GET /job-posting/{job_id}`: İş ilanı detaylarını alma
- `PUT /job-posting/{job_id}/parameters`: Eşleştirme parametrelerini güncelleme

### Eşleştirme

- `GET /match-candidates/{job_id}`: Bir iş için uygun adayları bulma
- `GET /job-posting/{job_id}/matches`: Bir iş için tüm eşleşmeleri alma

## Veri Modelleri

### İş İlanı
```python
{
    "title": str,  # İş başlığı
    "description": str,  # İş açıklaması
    "requirements": List[str],  # Gereksinimler
    "location": str,  # Konum
    "company": str,  # Şirket
    "matching_parameters": Optional[dict]  # Eşleştirme parametreleri
}
```

### Aday Eşleşmesi
```python
{
    "candidate_id": str,  # Aday ID
    "match_percentage": float,  # Eşleşme yüzdesi
    "missing_skills": List[str],  # Eksik beceriler
    "explanation": str  # Açıklama
}
```

## Katkıda Bulunma

1. Depoyu fork edin
2. Özellik dalı oluşturun
3. Değişikliklerinizi commit edin
4. Dalı push edin
5. Pull Request oluşturun

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.

## Teşekkürler

- NLP yetenekleri için spaCy
- Metin işleme için HuggingFace Transformers
- Verimli benzerlik araması için FAISS
- Web framework'ü için FastAPI
- Veri depolama için MongoDB
