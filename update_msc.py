import requests
import os
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.header import Header

# 1. КОНФИГУРАЦИЯ (Данные из твоих GitHub Secrets)
GIST_ID = os.getenv("GIST_ID")
GH_TOKEN = os.getenv("GH_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SMTP_USER = os.getenv("SMTP_USER")      
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") 

# ПОЛУЧАТЕЛЬ (Изменено по твоему запросу)
EMAIL_TO = "mrw.fortnite@mail.ru"

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
DISPLAY_NAME = "🏳️MSC VPN🗽WHITE LIST⚪"

def main():
    try:
        # --- ШАГ 1: ПОЛУЧЕНИЕ И ОБРАБОТКА ---
        print("Загрузка ключей...")
        resp = requests.get(SOURCE_URL)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        
        modified_content = [f"#profile-title: {DISPLAY_NAME}"]
        for line in lines:
            if line.strip():
                base_link = line.split('#')[0]
                modified_content.append(f"{base_link}#MSC%20VPN")
        
        final_content = "\n".join(modified_content)

        # --- ШАГ 2: ОБНОВЛЕНИЕ GIST ---
        print("Обновление Gist...")
        headers = {"Authorization": f"token {GH_TOKEN}"}
        gist_data = {"files": {"msc_vpn.txt": {"content": final_content}}}
        requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=gist_data).raise_for_status()

        # --- ШАГ 3: ССЫЛКИ И ТЕКСТ ---
        raw_url = f"https://gist.githubusercontent.com/raw/{GIST_ID}/msc_vpn.txt"
        encoded_name = urllib.parse.quote(DISPLAY_NAME)
        final_url = f"{raw_url}#{encoded_name}"
        
        msg_text = (
            "Добрый день!\n\n"
            "Ключи MSC VPN обновились.\n\n"
            "🔗 Ссылка для Happ / v2rayTun:\n"
            f"`{final_url}`\n\n"
            "Спасибо, что пользуетесь MSC VPN!"
        )

        # --- ШАГ 4: TELEGRAM ---
        print("Отправка в Telegram...")
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg_text, "parse_mode": "Markdown"})
        
        # --- ШАГ 5: ПОЧТА ---
        print(f"Отправка на почту {EMAIL_TO}...")
        email_msg = MIMEText(msg_text.replace('`', ''), 'plain', 'utf-8')
        email_msg['Subject'] = Header(f"Обновление {DISPLAY_NAME}", 'utf-8')
        email_msg['From'] = SMTP_USER
        email_msg['To'] = EMAIL_TO

        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [EMAIL_TO], email_msg.as_string())
        
        print("Успех! Скрипт выполнен полностью.")

    except Exception as e:
        print(f"Ошибка: {e}")

# ФИНАЛЬНАЯ ПРОВЕРКА СИНТАКСИСА
if __name__ == "__main__":
    main()
