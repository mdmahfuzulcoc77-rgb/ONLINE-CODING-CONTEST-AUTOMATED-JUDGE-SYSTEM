# core/context_processors.py
from .models import ContestSetting

def contest_deadline(request):
    setting = ContestSetting.objects.first() 
    if setting:
        return {'deadline': setting.end_time.isoformat()}
    return {'deadline': None}