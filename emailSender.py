import smtplib

def send(FROM,TO,SUBJECT,TEXT,SERVICE,PORT,USERNAME,PASSWORD): #string, list, string, string, string, string, string
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO),SUBJECT,TEXT)
    
    username = USERNAME #USERNAME
    password = PASSWORD #PASSWORD
    
    server = smtplib.SMTP(SERVICE, PORT) # 'smtp.gmail.com'
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(FROM,TO,message)
    server.quit()
