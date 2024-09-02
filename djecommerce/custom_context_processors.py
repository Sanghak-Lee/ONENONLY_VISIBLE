from decouple import config

def googleanalytics(request):
    return {
        'DEBUG' : config('DEBUG'),
        'google_tracking_id' : config('GOOGLE_TRACKING_ID')
    }