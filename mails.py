import smtplib

def translite(text):
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
               u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")

    tr = {ord(a):ord(b) for a, b in zip(*symbols)}
    return text.translate(tr)

def send_mail(text, to="izhur27@gmail.com"):
    from email.mime.text import MIMEText

    msg = MIMEText(text)
    msg['Subject'] = "New Sale. Beerroll"
    msg['From'] = "vlzhr.nots@gmail.com"
    msg['To'] = to 
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("vlzhr.nots", "!sushi!!!")

    server.sendmail("vlzhr.nots@gmail.com", to, msg.as_string())
    server.quit()
    return True
