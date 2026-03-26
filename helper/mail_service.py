import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Load env
load_dotenv()
BREVO_API_KEY = os.getenv("BREVO_MAIL_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")


def send_email(to_email, subject, content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": FROM_EMAIL, "name": "Water App"},
        subject=subject,
        html_content=content
    )

    try:
        response = api_instance.send_transac_email(email)
        print("Email sent:", response)
        return True
    except ApiException as e:
        print("Error:", e)
        return False

