from djoser.views import TokenCreateView
from djoser.conf import settings
from rest_framework import viewsets, mixins, status
from models.models import ChessGame
from models.serializers import ChessGameSerializer
from rest_framework.response import Response
from random import choice


class ChessGameViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin, viewsets.GenericViewSet):

    queryset = ChessGame.objects.all()
    serializer_class = ChessGameSerializer

    def create(self,request,*args,**kwargs):
			# Check if there are available games with a missing player
			available_games = ChessGame.objects.filter(whitePlayer__isnull=True) | ChessGame.objects.filter(blackPlayer__isnull=True)

			if available_games.exists():
				# Assign the current player as white or black randomly
				player_color = choice(['white', 'black'])
				
				# Set the game status as pending
				game_status = 'pending'
				
				# Create a new game with the assigned player color and status
				new_game = ChessGame.objects.create(**{player_color + 'Player': request.user, 'status': game_status})
				
				# Call the create method of the super class to save the game in the database
				return super().create(request, *args, **kwargs)
			else:
				# Find the game with a single assigned player
				game = ChessGame.objects.filter(whitePlayer__isnull=False, blackPlayer__isnull=False).exclude(status='pending').first()
				
				if game:
					# Change the game status to active
					game.status = 'active'
					
					# Assign the current user as the opposite player
					if game.whitePlayer == request.user:
						game.blackPlayer = request.user
					else:
						game.whitePlayer = request.user
					
					# Call the update method of the super class to save the changes
					return super().update(request, *args, **kwargs)
				else:
					# Delete any games with missing players or with a single player and status different from pending
					ChessGame.objects.filter(whitePlayer__isnull=True, blackPlayer__isnull=True).delete()
					ChessGame.objects.filter(whitePlayer__isnull=False, blackPlayer__isnull=False).exclude(status='pending').delete()
					
					# Return an error message
					return Response({'error': 'No available games found'}, status=status.HTTP_400_BAD_REQUEST)
      
		def update(self, request, *args, **kwargs):
			# Find the game with a single assigned player
			game = ChessGame.objects.filter(whitePlayer__isnull=False, blackPlayer__isnull=False).exclude(status='pending').first()

			if game:
				# Change the game status to active
				game.status = 'active'

				# Assign the current user as the opposite player
				if game.whitePlayer == request.user:
					game.blackPlayer = request.user
				else:
					game.whitePlayer = request.user

				# Call the update method of the super class to save the changes
				return super().update(request, *args, **kwargs)
			else:
				# Delete any games with missing players or with a single player and status different from pending
				ChessGame.objects.filter(whitePlayer__isnull=True, blackPlayer__isnull=True).delete()
				ChessGame.objects.filter(whitePlayer__isnull=False, blackPlayer__isnull=False).exclude(status='pending').delete()

				# Return an error message
				return Response({'error': 'No available games found'}, status=status.HTTP_400_BAD_REQUEST)
