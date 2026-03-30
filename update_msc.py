import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# Конфигурация (данные берутся из Секретов GitHub)
GIST_ID = os.getenv("GIST_ID")
GH_TOKEN = os.getenv("GH_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SMTP_USER = os.getenv("SMTP_USER")      # Твоя почта (отправитель)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # Пароль приложения (16 символов)

# Получатель
EMAIL_TO = "mrw.fortnite@mail.ru"

SOURCE_URL = "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt"
DISPLAY_NAME = "🏳️MSC VPN🗽WHITE LIST⚪"

def main():
    try:
        # 1. Загрузка
        resp = requests.get(SOURCE_URL)
        resp.raise_for_status()
        
        # 2. Обработка
        modified = [f"#profile-title: {DISPLAY_NAME}"]
        for line in resp.text.splitlines():
            if line.strip():
                modified.append(f"{line.split('#')[0]}#MSC%20VPN")
        
        # 3. Обновление Gist
        headers = {"Authorization": f"token {GH_TOKEN}"}
        gist_data = {"files": {"msc_vpn.txt": {"content": "\n".join(modified)}}}
        requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=gist_data).raise_for_status()

        # 4. Отправка TG
        msg = f"MSC VPN обновился: https://gist.githubusercontent.com/raw/{GIST_ID}/msc_vpn.txt"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})

        # 5. Отправка почты
        email_msg = MIMEText(msg, 'plain', 'utf-8')
        email_msg['Subject'] = Header("Обновление MSC VPN", 'utf-8')
        email_msg['From'] = SMTP_USER
        email_msg['To'] = EMAIL_TO

        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [EMAIL_TO], email_msg.as_string())
        
        print("Всё успешно отправлено!")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
