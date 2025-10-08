from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

@csrf_exempt
def upload_video(request):
    if request.method == 'POST':
        video_file = request.FILES.get('video')
        if video_file:
            # Save the file
            file_name = default_storage.save(f'videos/{video_file.name}', video_file)
            return JsonResponse({'success': True, 'filename': file_name})
        return JsonResponse({'error': 'No video file received'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405) 