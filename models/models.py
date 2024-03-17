from django.db import models

# Create your models here.
from rest_framework.views import APIView
from rest_framework.response import Response


class myClassView(APIView):


    def get(self, request):
        #Devuelve json ya que hereda APIView
        return Response({'message': 'Got some data!'})