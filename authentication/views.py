from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from patients.models import Patient
from cryptography.fernet import Fernet
import base64
from django.conf import settings
# import logging

# logger = logging.getLogger(__name__)

key = settings.ENCRYPTION_KEY.encode()
cipher_suite = Fernet(key)

def decrypt_field(encrypted_value):
    try:
        decrypted_value = cipher_suite.decrypt(base64.urlsafe_b64decode(encrypted_value)).decode()
        return decrypted_value
    except Exception as e:
        # logger.error(f"Error decrypting field: {e}")
        return JsonResponse({
            'success': False,
            'message': f'An error occurred during Decrypting: {str(e)}',
        })
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            all_emails = Patient.objects.values_list('email', flat=True)
            # logger.debug(f"All emails: {list(all_emails)}")

            if email in all_emails:
                user = Patient.objects.get(email=email)
                if user.check_password(password):
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Login successful. Welcome!'})
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Invalid password! Please try again.',
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Email Not Registerd! Please create an account first.',
                })
        except Exception as e:
            # logger.error(f"An error occurred during authentication: {e}")
            return JsonResponse({
                'success': False,
                'message': f'An error occurred during authentication: {str(e)}',
             })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
