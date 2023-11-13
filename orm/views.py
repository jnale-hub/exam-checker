
from django.shortcuts import render, redirect
from .forms import UploadForm 
from .ormscanner import orm_scanner
import os

def save_image(image, name, folder_path="images"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    image_path = os.path.join(folder_path, name)
    
    with open(image_path, 'wb') as destination:
        for chunk in image.chunks():
            destination.write(chunk)

def index(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            # Handle the form data, including the uploaded image and code
            image = request.FILES['image']
            name = form.cleaned_data['name']
            code = form.cleaned_data['code']

            # Rename the image to name
            image_name = f"{name}.png"

            save_image(image, image_name)

    
            # Using the code, communicate with the database to
            # get the answer_keys and the bubble_options
            # temporary data

            answer_key = {
                0: 3,
                1: 3,
                2: 3,
                3: 3,
                4: 3,
                5: 0,
                6: 1,
                7: 0,
                8: 2,
                9: 0,
                10: 3,
                11: 0,
                12: 0,
                13: 3,
                14: 0,
                15: 0,
                16: 2,
                17: 0,
                18: 1,
                19: 1
            }
            bubble_options = 4

            result, result_image, error = orm_scanner(image_name, answer_key, bubble_options)

            if error != None:
                return render(request, "orm/error.html", {
                    "error_message": error,
                })

            return render(request, "orm/result.html", {
                "name": name,
                "code": code,
                "result": result,
                # "result_image": result_image
            })

    else:
        form = UploadForm() 

    return render(request, "orm/index.html", {'form': form})


def result(request):
    return render(request, "orm/result.html")
