import smtplib
import time
from email.mime.text import MIMEText

from_email = input("введите вашу почту(Поддерживается яндекс и gmail): ")
password = input("Введите пароль от почты(прочтите readme.md перед тем, как вставлять): ")
emails_filename = "to_emails.txt"
print(f"Не забудьте вставить адреса почт, на которые надо отправить сообщение в файл {emails_filename}")
print("Не забудьте настроить вашу почту на работу с сервисами рассылки")
print("ведите текст письма в файл message.html")
subject = input("Введите тему письма")
with open("message.html") as file:
    body = file.read()
smtp_name = ""
if from_email.count("gmail.com") or from_email.count("yandex.ru"):
    if from_email.count("gmail.com"):
        smtp_name = 'smtp.gmail.com'
    else:
        smtp_name = 'smtp.yandex.ru'
# Создаем объект SMTP
server = smtplib.SMTP(smtp_name, 587)
# Указываем, что используем TLS
server.starttls()
# Авторизация на почте
server.login(from_email, password)
# Создаем сообщение
with open("message.html", encoding='utf-8') as file:
    message_text = file.read()
message = MIMEText(message_text, "html", "utf-8")
message["Subject"] = subject
message["From"] = from_email
with open(emails_filename, 'r', encoding='utf-8') as to_emails:
    for to_email in to_emails:
        try:
            # Добавляем адрес получателя в сообщение
            message["To"] = to_email
            # Отправляем письмо
            server.sendmail(from_email, to_email, message.as_string())
            print(f"Отправлено сообщение на {to_email}")
        except:
            print(f"Не отправлено на {to_email}\n Она валидна?")
        time.sleep(15)
# Закрываем соединение
server.quit()
