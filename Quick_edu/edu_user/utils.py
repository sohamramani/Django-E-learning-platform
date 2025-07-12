import logging


from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from minio import Minio
from twilio.rest import Client


logger = logging.getLogger(__name__)


# for sending otp on phone number using twilio
class MessageHandler:
    phone_number = None
    otp = None
    
    def __init__(self,phone_number,otp):
        self.phone_number = phone_number
        self.otp = otp
        
    def send_otp_on_phone(self):
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your OTP is {self.otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=self.phone_number
        )
        return message.sid


# for genrate presigned url and downloading resume file 
def download_file(request):
    try:
        # import pdb; pdb.set_trace()
        minioClient = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False  # Set to True if using HTTPS
        )

        # Generate pre-signed URL
        url = minioClient.get_presigned_url(
            "GET",
            settings.MINIO_MEDIA_FILES_BUCKET,
            request.user.userprofile.resume.name, 
        )

        logger.info(f"Download link generated for {request.user}: {url}")
        return redirect(url)
    except Exception as e:
        logger.error(f"Error generating download link: {e}   url : {url}" )
        messages.error(request, "Error generating download link.")
        return redirect('home')
    
    

class PaymentStatus:
    SUCCESS = "Success"
    FAILURE = "Failure"
    PENDING = "Pending"
    