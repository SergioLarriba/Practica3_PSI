from django.db import models

# Create your models here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import AbstractUser
import chess

class myClassView(APIView):


    def get(self, request):
        #Devuelve json ya que hereda APIView
        return Response({'message': 'Got some data!'})


class Player(AbstractUser):
    #Default user class, just in case we want to add something extra in he future
    # add extra fields here
    rating = models.IntegerField(default=0)

class ChessGame(models.Model):
    STATUS_CHOICES = [
        ('P','pending'),
        ('A','active'),
        ('F','finished')
    ]
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    board_state = models.TextField()  #Formato FEN
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    time_control = models.IntegerField()  #Tiempo por movimiento
    white_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='white_player')
    black_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='black_player')
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, related_name='winner', null=True)

    def __str__(self):
        board = chess.Board(self.board_state)  #Crea un tablero de ajedrez con el estado actual
        return f'Game {self.id}: {self.white_player.username} (White) vs {self.black_player.username} (Black) - Status: {self.get_status_display()}\n{board}'


#CASCADE: si se borra un jugador se borran todas las partidas en las que participa
#SET_NULL: si se borra un jugador se pone a null el campo winner

class ChessMove(models.Model):
    id = models.AutoField(primary_key=True)
    game = models.ForeignKey(ChessGame, on_delete=models.CASCADE, related_name='moves')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    move_from = models.CharField(max_length=2)
    move_to = models.CharField(max_length=2)
    promotion = models.CharField(max_length=1, null=True)

    def save(self, *args, **kwargs):
        if self.game.status != 'A':
            raise ValueError('LA partida no está activa, no se puede mover...')
        
        board = chess.Board(self.game.board_state)
        # Movimiento + Comprobación de si promociona
        move = chess.Move.from_uci(self.move_from + self.move_to + (self.promotion if self.promotion else ''))

        if move not in board.legal_moves:
            raise ValueError('Movimiento no válido')
        
        board.push(move)
        self.game.board_state = board.fen()

        super().save(*args, **kwargs)
        self.game.save()
        

    def __str__(self):
        return f'Player {self.player} Movement: {self.move_from} to {self.move_to} Promotion: {self.promotion}'