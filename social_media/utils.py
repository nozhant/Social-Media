import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from fcm.models import Device


def send_email(title, mess, receiver):
    mail_content = mess
    sender_gmail = 'helpglimpo@gmail.com'
    sender_pass = 'AdminVishal20@'
    message = MIMEMultipart()
    message['From'] = sender_gmail
    message['To'] = receiver
    message['Subject'] = title
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_gmail, sender_pass)
    text = message.as_string()
    session.sendmail(sender_gmail, receiver, text)
    session.quit()


'''
    for send notification to users
    inputs:
        title
        message
        phone
        {key: val}
'''
# def push_notification(title, message, phone, **kwargs):
#
#     devices = Device.objects.filter(name=phone)
#
#     data = {'click_action': 'FLUTTER_NOTIFICATION_CLICK'}
#     data.update(kwargs)
#
#     notif = {
#         'title': title,
#         'body': message,
#         'click_action': 'FLUTTER_NOTIFICATION_CLICK',
#         'sound': 'default',
#     }
#
#     for d in devices:
#         d.send_message(data=data, notification=notif)