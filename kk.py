# https://youtu.be/K21BSZPFIjQ
"""
Extract selected mails from your gmail account

1. Make sure you enable IMAP in your gmail settings
(Log on to your Gmail account and go to Settings, See All Settings, and select
 Forwarding and POP/IMAP tab. In the "IMAP access" section, select Enable IMAP.)

2. If you have 2-factor authentication, gmail requires you to create an application
specific password that you need to use. 
Go to your Google account settings and click on 'Security'.
Scroll down to App Passwords under 2 step verification.
Select Mail under Select App. and Other under Select Device. (Give a name, e.g., python)
The system gives you a password that you need to use to authenticate from python.

"""

# Importing libraries
import imaplib
import email
import json
import yaml  #To load saved login credentials from a yaml file

with open("credentials.yml") as f:
    content = f.read()
    
# from credentials.yml import user name and password
my_credentials = yaml.load(content, Loader=yaml.FullLoader)

#Load the user name and passwd from yaml file
user, password = my_credentials["user"], my_credentials["password"]

#URL for IMAP connection
imap_url = 'imap.gmail.com'

# Connection with GMAIL using SSL
my_mail = imaplib.IMAP4_SSL(imap_url)

# Log in using your credentials
my_mail.login(user, password)

# Select the Inbox to fetch messages
my_mail.select('Inbox')

#Define Key and Value for email search
#For other keys (criteria): https://gist.github.com/martinrusev/6121028#file-imap-search
#key = 'FROM'
# value = 'kevin@intouches.io'
# _, data = my_mail.search(None, key, value)  #Search for emails with specific key and value
result, data = my_mail.search(None, 'SUBJECT', '"Fwd: Session Notification:Rescheduled"')
mail_id_list = data[0].split()  

msgs = [] 
for num in mail_id_list:
    typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
    msgs.append(data)


result, scheduledata = my_mail.search(None, 'SUBJECT', '"Fwd: Session Notification:Scheduled"')
mail_id_list1 = scheduledata[0].split()  
msgs1 = [] 
for num in mail_id_list1:
    typ, data = my_mail.fetch(num, '(RFC822)') #RFC822 returns whole message (BODY fetches just body)
    msgs1.append(data)


#Now we have all messages, but with a lot of details
#Let us extract the right text and print on the screen

#In a multipart e-mail, email.message.Message.get_payload() returns a 
# list with one item for each part. The easiest way is to walk the message 
# and get the payload on each part:
# https://stackoverflow.com/questions/1463074/how-can-i-get-an-email-messages-text-content-using-python

# NOTE that a Message object consists of headers and payloads.
    

schedule = []
reschedule = []

for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg=email.message_from_bytes((response_part[1]))
            for part in my_msg.walk():  
                if part.get_content_type() == 'text/plain':
                    text = part.get_payload().split("Dear")
                    if(len(text)>1):
                        text = part.get_payload().split("Dear")[1]
                    firstpart = text.split('/')[0]
                    month = firstpart[len(firstpart)-1]
                    day = text.split('/')[1]
                    year = text.split('/')[2][0:4]

                    if year.strip().isdigit() == False:
                        month = text.split('/')[1]
                        day = text.split('/')[2][0]
                        year = firstpart[len(firstpart)-4:len(firstpart)]

                    start_part = text.split(":")[0]
                    start_time_hour = start_part[len(start_part)-1]
                    start_time_minute = text.split(":")[1][0:2]
                    # print(month,day,year,start_time_hour,start_time_minute)
                    if(int(month)<10): month = "0"+month
                    if(int(day)<10): day = '0'+ day
                    date = year+'-'+month+'-'+day    
                    reschedule.append(date)
print(reschedule)


for msg in msgs1[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg=email.message_from_bytes((response_part[1]))
            for part in my_msg.walk():  
                if part.get_content_type() == 'text/plain':

                    text = part.get_payload().split("Dear")
        
                    if(len(text)>1):
                        text = part.get_payload().split("Dear")[1]
                    else:
                        text = part.get_payload().split("Dear")[0]
                    # print(text)
                    firstpart = text.split('/')[0]
                    month = firstpart[len(firstpart)-1]
                    day = text.split('/')[1]
                    year = text.split('/')[2][0:4]
                    if year.strip().isdigit() == False:
                        month = text.split('/')[1]
                        day = text.split('/')[2][0]
                        year = firstpart[len(firstpart)-4:len(firstpart)]

                    start_part = text.split(":")[0]
                    start_time_hour = start_part[len(start_part)-1]
                    start_time_minute = text.split(":")[1][0:2]

                    print(month,day,year,start_time_hour,start_time_minute)
                    if(int(month)<10): month = "0"+month
                    if(int(day)<10): day = '0'+ day
                    date = year+'-'+month+'-'+day

                    print(text[text.find("(")+1:text.find(")")])    
                    schedule.append({
                        "title" : start_time_hour + " : "+ start_time_minute + "   "+text[text.find("(")+1:text.find(")")].strip(),
                        "start": date
                    })
print(schedule)
print(reschedule)           


with open('events.json', 'w') as f:
    json.dump(schedule, f)

# Dear Jiazheng Chen,

# You have a class on 2/19/2024, 2:00 AM to 2/19/2024, 3:00 AM  in
# (GMT+08:00) China Standard Time (Asia/Shanghai) with Chenhao Chenhao He =E4=
# =BD=95=E9=99=88=E7=81=8F.

# The Class has been Rescheduled.

# Note: if the class is rescheduled, then you will be receiving a new email
# about the new class time.

# Regards,
# Wang
