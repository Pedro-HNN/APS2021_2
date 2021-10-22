from django.shortcuts import render
from main.camera import RegistrationCamera,LoginCamera
from django.contrib import messages

# Create your views here.
def index(response):
    return render(response, "main/main.html")

def register(request):
    if request.method == 'GET':
        return render(request, "main/register.html")

def login(request):
    if request.method == 'GET':
        return render(request, "main/login.html")

def registerFace(request):
    if request.method == 'POST':
        if request.POST.get('name',None) == "" or request.POST.get('email', None) == "":
            return render(request, "main/register.html", {'message': "Digite seu nome e email dentro dos campos selecionados!"})
        else:
            register = RegistrationCamera(request)

            if register.getValidEmail():
                if register.getValidFace():
                    values = register.getValues()
                    return render(request,"main/info.html",{'name': values[0],'email':values[1],'level':values[2]})
                else:
                    return render(request, "main/register.html", {'message': "Face já registrada no banco de dados!"})
            else:
                return render(request, "main/register.html",{'message':"Email não válido!"})

    if request.method == 'GET':
        return render(request, "main/register.html")

def loginFace(request):
    if request.method == 'POST':
        login = LoginCamera()

        if login.getTheresFace():
            if login.getValid():
                values = login.getValues()
                return render(request,"main/info.html",{'name': values[0],'email':values[1],'level':values[2]})
            else:
                return render(request, "main/login.html", {'message': "Face não encontrada no banco de dados!"})
        else:
            return render(request, "main/login.html", {'message': "Não há nenhuma face no nosso banco de dados!"})

    if request.method == 'GET':
        return render(request, "main/login.html")


