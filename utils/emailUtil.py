"""邮件发送工具"""
import smtplib
from email.message import EmailMessage

from config import get_settings


def send_email(content: str, subject: str, from_email: str, to_email: str, subtype='text'):
    setting = get_settings()
    msg = EmailMessage()
    msg.set_content(content, subtype=subtype, charset='utf-8')

    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    with smtplib.SMTP_SSL(setting.smtp_server, setting.smtp_port) as server:
        server.login(setting.smtp_username, setting.smtp_password)
        server.send_message(msg)
