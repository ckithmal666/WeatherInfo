import datetime
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from .models import *
from .models import City
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Account was created')
            return redirect('login')

    context = {'form':form}
    return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Incorrect  Username or Password')
        
    context = {}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def aboutMe(request):
    
    context = {
        'subtitle': 'About',
        'content': 'Welcome to WeatherInfo web application, your go-to destination for accurate and up-to-date weather predictions. Get started by exploring our weather forecasts for your location. If you have any questions, suggestions, or concerns, feel free to contact me at ckithmal666@gmail.com.', 
    }
    return render(request, 'about.html', context)
    

@login_required(login_url='login')
def index(request):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid=271d1234d3f497eed5b1d80a07b3fcd1&units=imperial'
    city = 'Dublin'

    cities = City.objects.all()

    weather_data = []

    for city in cities:

        r = requests.get(url.format(city)).json()
        
        city_weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        weather_data.append(city_weather)
    
    print(weather_data)
    context = {'weather_data' : weather_data}
    return render(request, 'weather/index.html', context)

def prediction(request):
    API_KEY = "271d1234d3f497eed5b1d80a07b3fcd1"
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alarts&appid={}"
    #forecast_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"


    if request.method == "POST":
        city1 = request.POST['city1']

        weather_data1, dailly_forecast1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_url)

        context = {

            "weather_data1" : weather_data1,
            "daily_forecast1" : dailly_forecast1
        }

        return render(request, "prediction.html", context)
    else:
        return render(request, "prediction.html")

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    weather_data = {
        "city" : city,
        "temperature" : round(response['main']['temp'] - 273.15, 2),
        "description" : response['weather'][0]['description'],
        "icon" : response['weather'][0]['icon']
    }

    daily_forecasts = []
    for daily_data in forecast_response['daily'][:5]:
        daily_forecasts.append({
            "day": datetime.datetime.fromtimestamp(daily_data['dt']).strftime("%A"),
            "min_temp": round(daily_data['temp']['min'] - 273.15, 2),
            "max_temp": round(daily_data['temp']['max'] - 273.15, 2),
            "description": daily_data['weather'][0]['description'],
            "icon": daily_data['weather'][0]['icon']
        })

    return weather_data, daily_forecasts
