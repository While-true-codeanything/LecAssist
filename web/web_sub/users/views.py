from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'users/main_page.html')


def open_login(request):
    return render(request, 'users/login.html')


def open_register(request):
    return render(request, 'users/registration.html')


def open_upload_page(request):
    return render(request, 'users/upload.html')


def upload_video(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['video_file']
        # Вы можете сохранить файл или обработать его здесь
        # Например:
        # with open('some_path/video.mp4', 'wb+') as destination:
        #     for chunk in uploaded_file.chunks():
        #         destination.write(chunk)
        return HttpResponse('Файл успешно загружен')
    return render(request, 'upload.html')