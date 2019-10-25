import os
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendDiffMail(site, out_filename, counters):
    changed_desc = counters['changed_desc']
    new_found_pages = counters['new_found_pages']
    new_lost_pages = counters['new_lost_pages']
    changed_status_code = counters['changed_status_code']
    changed_indexation = counters['changed_indexation']
    changed_title = counters['changed_title']
    changed_desc = counters['changed_desc']
    changed_h1 = counters['changed_h1']
    changed_h2 = counters['changed_h2']
    changed_canonical = counters['changed_canonicals']
    subject = f"Here is your Diff Report for {site}"
    body = f"""
                <h2>New changes</h2>
                    <p>
                        <strong>New found pages: </strong> {new_found_pages}
                        <hr/>
                        <strong>New lost pages: </strong> {new_lost_pages}
                        <hr/>
                        <strong>Changed Status Code: </strong> {changed_status_code}
                        <hr/>
                        <strong>Changed Indexation: </strong> {changed_indexation}
                        <hr/>
                        <strong>Changed Title: </strong> {changed_title}
                        <hr/>
                        <strong>Changed descriptions: </strong> {changed_desc}
                        <hr/>
                        <strong>Changed H1: </strong> {changed_h1}
                        <hr/>
                        <strong>Changed H2: </strong> {changed_h2}
                        <hr/>
                        <strong>Changed Canonicals: </strong> {changed_canonical}
                    </p>
            """
    sender_email = 'SF Cloud Robot <noreply@robot.cloud>'
    receiver_email = 'Your Name <your.name@email.com>'

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    #message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "html"))

    filename = out_filename  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "vnd.ms-excel")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    try:
        server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465)
        server.ehlo()
        server.login('apikey', os.environ.get('SENDGRID_API_KEY'))
        server.sendmail(sender_email, receiver_email, text)
        server.close()
        print("mail sent")
    except Exception as e:
        print(e)