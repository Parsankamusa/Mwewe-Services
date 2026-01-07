import requests
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from models import NotificationTemplate



def get_notification_template(template_type, **variables):
    """Fetch notification template from database."""
    try:

        template = NotificationTemplate.objects.get(
            template_type=template_type,
            is_active=True
        )
        content = template.content.format(**variables)
        subject = template.subject.format(**variables) if template.subject else ""
        return {
            'content': content,
            'subject': subject,
            'is_html': template.is_html
        }
    except (NotificationTemplate.DoesNotExist, KeyError):
        return None


def send_mail(mail, content, subj, html=False):
    """Send email via SMTP."""
    SMTPserver = 'smtppro.zoho.com'
    sender = 'admin@mwewe.co.ke'
    USERNAME = "admin@mwewe.co.ke"
    PASSWORD = "Opendoor@24"

    text_subtype = 'html' if html else 'plain'

    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject'] = subj
        msg['From'] = sender

        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, [mail], msg.as_string())
            print(f"Email sent successfully to {mail}")
        finally:
            conn.quit()
    except Exception as e:
        print(f"Error sending email to {mail}: {str(e)}")
        raise


def send_sms_staff(phone, message):
    """Send SMS to staff member."""
    template_data = get_notification_template(
        'staff_notification_sms',
        message=message,
        phone=phone
    )

    if template_data:
        message = template_data['content']

    url = "https://sendsms.dibon.co.ke/api/messaging/sendsms"
    api_key = "YOUR_API_KEY"  # Move to settings

    payload = {
        "from": "MWEWE LTD",
        "to": f"254{phone}",
        "message": message
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    req = requests.post(url, headers=headers, json=payload)
    print(req.text)


def send_sms_client(phone, next_due_date, client_name):
    """Send reminder SMS to client."""
    url = "https://sendsms.dibon.co.ke/api/messaging/sendsms"
    api_key = "YOUR_API_KEY"  # Move to settings

    payload = {
        "from": "MWEWE LTD",
        "to": f"254{phone}",
        "message": (
            f"Hello {client_name.company_name}, your "
            f"{client_name.services_required} is due on {next_due_date}.\n\n"
            "Thank you."
        )
    }
    headers = {
        'Authorization': f"Bearer {api_key}",
        'Content-Type': "application/json"
    }

    req = requests.post(url, headers=headers, json=payload)
    print(req.text)
