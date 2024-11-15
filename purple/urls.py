from tkinter.font import names

from django.urls import path
from . views import *

urlpatterns=[
    path('register/', RegisterView.as_view(), name='register'),

]