import smtplib

from_email = input("введите вашу почту(Поддердивается яндекс и gmail)")
password = input("Введите пароль от почты")
filename = "to_emails.txt"
print(f"Не забудьте вставить адреса почт, на которые надо отправить сообщение в файл {filename}")
print("Не забудьте настроить вашу почту на работу с сервисами рассылки")
subject = input("Введите тему письма")
body = input("ведите текстписьма")
smtp_name = ""
if from_email.count("gmail.com") or from_email.count("yandex.ru"):
    if from_email.count("gmail.com"):
        smtp_name = 'smtp.gmail.com'
    else:
        smtp_name = 'smtp.yandex.ru'
with open(filename, 'r', encoding='utf-8') as to_emails:
    for to_email in to_emails:
        # Создаем объект SMTP
        server = smtplib.SMTP(smtp_name, 587)

        # Указываем, что используем TLS
        server.starttls()

        # Авторизация на почте
        server.login(from_email, password)

        # Создаем сообщение
        message = f"From: {from_email} Subject: {subject}\n\n{body}"
        # Отправляем письмо
        server.sendmail(from_email, to_email, message.encode('utf-8'))

        # Закрываем соединение
        server.quit()
