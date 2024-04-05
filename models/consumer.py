import json
import chess 

from models.models import *
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token
# async_to_sync 
from asgiref.sync import async_to_sync
import pdb 

class ChessConsumer(WebsocketConsumer):
    
    # 1º Petición -> acceder a la pagina  
    def connect(self):
        self.gameID = self.scope['url_route']['kwargs']['gameID']
        self.room_group_name = str(self.gameID)  
        self.token_key = self.scope['query_string'].decode()    
        
        # Join room group
        async_to_sync(self.accept()) 
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        
        # Comprueba si el token es válido 
        if self.validate_token(self.token_key) is False:
            async_to_sync(self.send(text_data = json.dumps({
                'type': 'error', 
                'message': 'Invalid token. Connection not authorized.'
            }))) 
            async_to_sync(self.close()) 
            return
        
        # Comprueba si el game id es válido 
        if not ChessGame.objects.filter(id=self.room_group_name).exists():
            async_to_sync(self.send(text_data = json.dumps({
                'type': 'error', 
                'message': f'Invalid game with id {self.room_group_name}'
            }))) 
            async_to_sync(self.close()) 
            return
        
        self.user_id = self.get_token_from_user(self.token_key)
        # Comprueba si el usuario es válido del game_id 
        if self.validate_user_in_game(self.gameID) is False:
            async_to_sync(self.send(text_data = json.dumps({
                'type': 'error', 
                'message': f'Invalid game with id {self.gameID}'
            }))) 
            async_to_sync(self.close()) 
            return
        

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        
        # Enviar un mensaje después de aceptar la conexión
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'game',
            'message': 'OK',
            'status': 'connected',
            'playerID': self.user_id 
        }))) 
        return 
        
        
    def disconnect(self, close_code):
        """ 
        This method is called when the WebSocket connection is closed. 
        It removes the channel from the room group.
        """
        
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)

    
    # 2º Peticion y cualquiera -> la maneja receive 
    def receive(self, text_data):
        # pdb.set_trace() 
        data = json.loads(text_data)
        message_type = data.get('type')
        
        game = ChessGame.objects.get(id=self.gameID)

        if message_type == 'move':
            # Extraccion de los datos 
            _from = data.get('from')
            to = data.get('to')
            playerID = data.get('playerID')
            promotion = data.get('promotion')

            # Si el movimiento es válido, lo almacena en la base de datos
            try:
                player = Player.objects.get(id=self.user_id)
                game = ChessGame.objects.get(id=self.gameID)
                chess_move = ChessMove(move_from=_from, move_to=to, game=game, player=player, promotion=promotion)
                chess_move.save()
            except Exception as e:
                # Si hay un error al guardar el movimiento, envía un mensaje de error
                async_to_sync(self.channel_layer.group_send(({
                   self.room_group_name,
                    {
                        'type': 'move_cb',
                        'content': {
                            'type': 'error',
                            'from': _from,
                            'to': to,
                            'playerID': playerID,
                            'promotion': promotion 
                        }
                    }
                })))
                return

            # Envía el movimiento a todos los jugadores en el mismo juego
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'move_cb',
                    'content':
                    {
                        'type': 'move',
                        'from': _from,
                        'to': to,
                        'playerID': playerID,
                        'promotion': promotion 
                    }
                }
            )

        return
            
    def game_cb(self, event):
        """ This method is called when the server sends a message to the WebSocket 
        connection. It sends the message to the client. 
        """
        
        message = event['content']['message']
        status = event['content']['status']
        playerID = event['content']['playerID'] 
        
        # Send message to WebSocket
        async_to_sync(self.send(text_data=json.dumps({
            self.room_group_name,{
                'type': 'game',
                'message': message, 
                'status': status,
                'playerID': playerID
            }
        })))
        
    def move_cb(self, event):
        # Extrae los detalles del movimiento del evento
        _from = event['content']['from']
        to = event['content']['to']
        playerID = event['content']['playerID']
        promotion = event['content']['promotion']
    
        # Envía el movimiento a todos los jugadores en el mismo juego
        async_to_sync(self.send(text_data=json.dumps({
            'type': 'move',
            'from': _from,
            'to': to,
            'playerID': playerID,
            'promotion': promotion
        })))
    
    # Obtener user_id a partir del token
    def get_token_from_user(self, token_key):
        try: 
            token = Token.objects.get(key=token_key)
            return token.user_id
        except Token.DoesNotExist:
            return None
    
    # Comprobar si el token es válido 
    def validate_token(self, token_key):
        return Token.objects.filter(key=token_key).exists()
    
    # Comprobar si el usuario en el game es valido 
    def validate_user_in_game(self, game_id): 
        if ChessGame.objects.filter(id=game_id, whitePlayer=self.user_id).exists() or \
        ChessGame.objects.filter(id=game_id, blackPlayer=self.user_id).exists():
            return True
        return False
            
        
            
        
    
