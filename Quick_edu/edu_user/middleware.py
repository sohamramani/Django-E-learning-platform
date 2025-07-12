import logging

from .models import RequestLog
from django.contrib import messages
from django.shortcuts import redirect
from time import gmtime, strftime


logger = logging.getLogger(__name__)


# log user activity if loged in 
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        if request.user.is_authenticated:
            log_entry = RequestLog( 
                    user=request.user,
                    path=request.path,
                    method=request.method
                )
            log_entry.save()
            logger.info(f"User: {request.user.username}, Path: {request.path}, Method: {request.method}, time: {showtime}")
        else:
            logger.info(f"Anonymous user, Path: {request.path}, Method: {request.method}, time: {showtime}")
        response = self.get_response(request)
        return response
    
    def process_response(self, request, response):
        print(f"Response Status Code: {response.status_code}")
        return response
    

#  role based admin panal access 
class RoleBasedAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'): 
            if request.user.is_authenticated:
                if not request.user.is_superuser:
                    logger.warning(f"Unauthorized access attempt by {request.user.username} to admin page.")
                    messages.error(request, "You are not authorized to access this page.")
                    return redirect('home')
            else:
                messages.error(request, "you have to login first to access this page. ")
                return redirect('login')
        response = self.get_response(request)
        return response
