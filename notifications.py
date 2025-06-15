import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import os
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

class NotificationService:
    def __init__(self):
        """
        E-posta ve SMS kimlik bilgileriyle bildirim servisini başlat
        """
        # E-posta yapılandırması
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # SMS yapılandırması
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Kimlik bilgileri varsa Twilio istemcisini başlat
        if all([self.twilio_account_sid, self.twilio_auth_token]):
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """
        E-posta bildirimi gönder
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = to_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"E-posta gönderilirken hata oluştu: {str(e)}")
            return False
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        """
        Twilio kullanarak SMS bildirimi gönder
        """
        if not self.twilio_client:
            print("Twilio istemcisi başlatılmamış. Kimlik bilgilerinizi kontrol edin.")
            return False
            
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_phone
            )
            return True
        except Exception as e:
            print(f"SMS gönderilirken hata oluştu: {str(e)}")
            return False
    
    def send_match_notification(
        self,
        candidate_email: str,
        candidate_phone: Optional[str],
        match_data: Dict
    ) -> Dict:
        """
        E-posta ve/veya SMS ile eşleşme bildirimi gönder
        """
        results = {"email": False, "sms": False}
        
        # Bildirim içeriğini hazırla
        subject = "Yeni İş Eşleşmesi Bulundu!"
        email_body = f"""
        <h2>Yeni İş Eşleşmesi Bulundu!</h2>
        <p>Profilinize uygun bir iş bulduk:</p>
        <ul>
            <li>Eşleşme Yüzdesi: {match_data['match_percentage']}%</li>
            <li>Eksik Beceriler: {', '.join(match_data['missing_skills']) if match_data['missing_skills'] else 'Yok'}</li>
        </ul>
        <p>Detayları görmek için lütfen hesabınıza giriş yapın.</p>
        """
        
        sms_message = f"Yeni iş eşleşmesi bulundu! Eşleşme yüzdesi: {match_data['match_percentage']}%. Detaylar için giriş yapın."
        
        # E-posta gönder
        if candidate_email:
            results["email"] = self.send_email(candidate_email, subject, email_body)
        
        # Telefon numarası varsa SMS gönder
        if candidate_phone and self.twilio_client:
            results["sms"] = self.send_sms(candidate_phone, sms_message)
        
        return results 