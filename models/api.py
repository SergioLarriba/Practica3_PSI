from djoser.views import TokenCreateView
from djoser.conf import settings
from rest_framework import viewsets, mixins, status
from models.models import ChessGame
from models.serializers import ChessGameSerializer
from rest_framework.response import Response
from random import choice


#Añadir user_id y rating a la respuesta ya que djoser no lo ofrece por defecto
class MyTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        response = super()._action(serializer)
        tokenString = response.data['auth_token']
        tokenObject = settings.TOKEN_MODEL.objects.get(key=tokenString)
        response.data['user_id'] = tokenObject.user.id
        response.data['rating'] = tokenObject.user.rating
        return response


# Create your models here.
class ChessGameViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):

    queryset = ChessGame.objects.all()
    serializer_class = ChessGameSerializer

    #Override create method
    def create(self,request,*args,**kwargs):
        #Comprobar si hay una partida disponible
        game = ChessGame.objects.filter(status='pending').first()
        if game:
            #Si hay una partida disponible, unir al usuario a ella
            if game.whitePlayer:
                game.blackPlayer = request.user
            else:
                game.whitePlayer = request.user
            #Cambiar el estado de la partida
            game.status = 'A'
            game.save()
            #Serializar los datos y devolverlos
            serializer = self.get_serializer(game)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            game = ChessGame.objects.filter(status='A').first()
            if game:
                return Response({'detail':'Game is not pending'},status=status.HTTP_400_BAD_REQUEST)
            else:
                #Crear una partida nueva y establecer estado a pending
                mutable_data = request.data.copy()
                mutable_data['status'] = 'P'
                #Asignar aleatoriamente el color
                if choice([True,False]):
                    mutable_data['whitePlayer'] = request.user.id
                else:
                    mutable_data['blackPlayer'] = request.user.id
                request._full_data = mutable_data
                #Llamar al metodo create de la clase padre
                #return super().create(request,*args,**kwargs)   
                response = super().create(request,*args,**kwargs)
                return Response(response.data, status=status.HTTP_201_CREATED)  #Test 5 y 6 fallan, esperan 200

    #Override update method
    def update(self,request,*args,**kwargs):
        #Comprobar si el juego esta disponible
        game = self.get_object()
        if game.status != 'P':
            return Response({'detail':'Game is not pending'},status=status.HTTP_400_BAD_REQUEST)
        #Comprobar si el usuario esta en el juego
        if game.whitePlayer != request.user and game.blackPlayer != request.user:
            return Response({'detail':'User is not in the game'},status=status.HTTP_400_BAD_REQUEST)
        #ACtualizar el juego
        if game.whitePlayer == request.user:
            game.blackPlayer = request.user
        else:
            game.whitePlayer = request.user
        game.status = 'A'
        game.save()
        serializer = self.get_serializer(game)
        return Response(serializer.data,status=status.HTTP_200_OK)
