from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import send_email 
from patients.models import Patient
from clinician.models import Doctor
import pyotp  # Ensure you have pyotp installed

# def generate_and_send_2fa_code(user):
#     if not user.otp_secret:
#         user.generate_otp_secret()
#     totp = pyotp.TOTP(user.otp_secret)
#     otp_code = totp.now()
#     subject = "Your 2FA Code"
#     html_content = f"<p>Your 2FA code is: {otp_code}</p>"
#     send_email(subject, user.email, html_content)
def generate_and_send_2fa_code(user):
    user.generate_and_store_otp_code()
    otp_code = user.otp_code
    subject = "Your 2FA Code"
    html_content = f"<p>Your 2FA code is: {otp_code}</p>"
    send_email(subject, user.email, html_content)

@csrf_exempt
def resend_2fa_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')

        # Fetch user object based on email
        user = Patient.objects.filter(email=email).first() or Doctor.objects.filter(email=email).first()

        if user:
            generate_and_send_2fa_code(user)
            return JsonResponse({'success': True, 'message': '2FA code resent successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'User not found.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            all_emails = Patient.objects.values_list('email', flat=True)

            if email in all_emails:
                user = Patient.objects.get(email=email)
                if user.check_password(password):
                    # Check if 2FA is enabled
                    if user.enable_2fa:
                        generate_and_send_2fa_code(user)
                        return JsonResponse({'success': True, 'message': '2FA code sent'})
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Login successful. Welcome!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Invalid password! Please try again.'})
            else:
                return JsonResponse({'success': False, 'message': 'Email Not Registered! Please create an account first.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred during authentication: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def password_reset_request(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get('email')
        patient = Patient.objects.filter(email=email).first()
        doctor = Doctor.objects.filter(email=email).first()
        user = patient or doctor
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f'http://localhost:3000/onboarding/welcome-to-medlink/auth/password/reset/?uid={uid}&token={token}'
            subject = "Password Reset Link"
            html_content = f"<p>Click <a href='{reset_link}'>here</a> to reset your password.</p>"

            email_sent = send_email(subject, email, html_content)
            if email_sent:
                return JsonResponse({'success': True, 'message': 'Password reset email sent.'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again'})
        else:
            return JsonResponse({'success': False, 'message': 'Email not found.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
@csrf_exempt
def password_reset_confirm(request, uidb64, token):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            
            if not password or not confirm_password:
                return JsonResponse({'error': 'Missing fields'}, status=400)
                
            if password != confirm_password:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            uid = force_str(urlsafe_base64_decode(uidb64))
            patient = Patient.objects.filter(pk=uid).first()
            doctor = Doctor.objects.filter(pk=uid).first()
            user = patient or doctor

            if user and default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return JsonResponse({'message': 'Password has been reset'})
            return JsonResponse({'error': 'Invalid token'}, status=400)
        except (TypeError, ValueError, OverflowError, Patient.DoesNotExist, Doctor.DoesNotExist, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid token or request'}, status=400)
    return HttpResponse(status=405)

@csrf_exempt
def verify_2fa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp_code = data.get('code')

            user = Patient.objects.filter(email=email).first() or User.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'success': False, 'message': 'User not found!'})

            if user.verify_otp(otp_code):
                login(request, user)
                return JsonResponse({'success': True, 'message': '2FA verified successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid 2FA code'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})






# from django.contrib.auth import authenticate, login
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from patients.models import Patient
# from cryptography.fernet import Fernet
# import base64
# from django.conf import settings
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.template.loader import render_to_string
# from django.http import JsonResponse, HttpResponse
# from patients.models import Patient
# from doctors.models import Doctor
# from django.views.decorators.csrf import csrf_exempt
# from .utils import send_email 

# # logger = logging.getLogger(__name__)

# key = settings.ENCRYPTION_KEY.encode()
# cipher_suite = Fernet(key)

# def decrypt_field(encrypted_value):
#     try:
#         decrypted_value = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_value)).decode()
#         return decrypted_value
#     except Exception as e:
#         # logger.error(f"Error decrypting field: {e}")
#         return JsonResponse({
#             'success': False,
#             'message': f'An error occurred during Decrypting: {str(e)}',
#         })
# @csrf_exempt
# def login_view(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             password = data.get('password')

#             all_emails = Patient.objects.values_list('email', flat=True)

#             if email in all_emails:
#                 user = Patient.objects.get(email=email)
#                 if user.check_password(password):
#                     # Check if 2FA is enabled
#                     if user.enable_2fa:
#                         return JsonResponse({'success': True, 'message': '2FA required'})
#                     login(request, user)
#                     return JsonResponse({'success': True, 'message': 'Login successful. Welcome!'})
#                 else:
#                     return JsonResponse({
#                         'success': False,
#                         'message': 'Invalid password! Please try again.',
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': 'Email Not Registered! Please create an account first.',
#                 })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'message': f'An error occurred during authentication: {str(e)}',
#              })

#     return JsonResponse({'success': False, 'message': 'Invalid request method'})

# @csrf_exempt
# def password_reset_request(request):
#     if request.method == "POST":

#         data = json.loads(request.body)
#         email = data.get('email')
#         patient = Patient.objects.filter(email=email).first()
#         doctor = Doctor.objects.filter(email=email).first()
#         user = patient or doctor
#         if user:
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             # if user == patient:
                
#             reset_link = f'http://localhost:3000/onboarding/welcome-to-medlink/auth/password/reset/?uid={uid}&token={token}'
#             subject = "Password Reset Link"
#             html_content = f"<p>Click <a href='{reset_link}'>here</a> to reset your password.</p>"

#             email_sent = send_email(subject, [email], html_content)
#             try:
#                 if email_sent:
#                     return JsonResponse({'success': True, 'message': 'Password reset email sent.'})
#                 else:
#                     return JsonResponse({'success': False, 'message': 'Our Bad! Failed to send email. Please try again'})
#             except Exception as e:
#                 return JsonResponse({'success':False, 'message':str(e)})
            
#         else:
#             return JsonResponse({'success': False, 'message': 'Email not found.'})
#     else:
#         return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
# @csrf_exempt
# def password_reset_confirm(request, uidb64, token):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             password = data.get('password')
#             confirm_password = data.get('confirm_password')
            
#             if not password or not confirm_password:
#                 return JsonResponse({'error': 'Missing fields'}, status=400)
                
#             if password != confirm_password:
#                 return JsonResponse({'error': 'Passwords do not match'}, status=400)

#             uid = force_str(urlsafe_base64_decode(uidb64))
#             patient = Patient.objects.filter(pk=uid).first()
#             doctor = Doctor.objects.filter(pk=uid).first()
#             user = patient or doctor

#             if user and default_token_generator.check_token(user, token):
#                 user.set_password(password)
#                 user.save()
#                 return JsonResponse({'message': 'Password has been reset'})
#             return JsonResponse({'error': 'Invalid token'}, status=400)
#         except (TypeError, ValueError, OverflowError, Patient.DoesNotExist, Doctor.DoesNotExist, json.JSONDecodeError):
#             return JsonResponse({'error': 'Invalid token or request'}, status=400)

#     return HttpResponse(status=405)

# @csrf_exempt
# def verify_2fa(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get('email')
#             code = data.get('code')

#             user = Patient.objects.filter(email=email).first()

#             if user and user.enable_2fa:
#                 # Replace this with actual 2FA code validation logic
#                 if validate_2fa_code(email, code):  # Implement this function to verify the code
#                     login(request, user)
#                     return JsonResponse({'success': True, 'message': '2FA verified successfully'})
#                 else:
#                     return JsonResponse({'success': False, 'message': 'Invalid 2FA code'}, status=400)

#             return JsonResponse({'success': False, 'message': '2FA is not enabled or user not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': f'An error occurred during 2FA verification: {str(e)}'}, status=500)
    
#     return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)
