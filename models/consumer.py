import websocket
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
from channels.generic.websocket import WebsocketConsumer
import asyncio
import chess


class Consumer(AsyncWebsocketConsumer):

    #Ejecuta cuando establece conexion WebSocket, verifica token y registra user, si token invalido cierra conexion
    async def connect(self,token,user):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        #Compruebo token
        if not await self.verify_token(token):
            await self.close(code=444)  #444 codigo de error personalizado
            return

        #Registro usuario
        if not await self.register_user(user):
            await self.close(code=445)  #445 codigo de error personalizado
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name #Creado automaticamente por channels
        )

        #Se controla el acceso aqui
        await self.accept()

    # Verifica token
    async def verify_token(self, token):
        await self.send(text_data=json.dumps({'token': token}))
        response = await self.receive()
        return json.loads(response['text'])['status'] == 'ok'


    # Registra usuario
    async def register_user(self, user):
        await self.send(text_data=json.dumps({'topic': self.topic, 'user': user}))
        response = await self.receive()
        return json.loads(response['text'])['status'] == 'ok' 



    #Si recibe "move" valida el movimiento y lo almacena. Luego lo envia y verifica si finaliza la partida
    def receive(self, message):
        data = json.loads(message)
        message_type = data['message']

        #En caso de que el mensaje sea "move", lo valida y envia a todos los jugadores (channel_layer)
        #Luego verifica si la partida ha finalizado usar python-chess
        if message_type == "move":
            move_data = data.get('move_data')
            if move_data:
                #Validar y almacenar movimiento
                await self.process_move(move_data)
            else:
                await self.send_error("Invalid move message")
        else:
            await self.send_error("Invalid message type")


    #Procesa el movimiento, lo valida y lo almacena
    async def process_move(self, move_data):
        try:
            move = chess.Move.from_uci(move_data['move'])
            if move in self.board.legal_moves:
                self.board.push(move)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'send_move',
                        'message': move_data
                    }
                )
                if self.check_game_end():
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_end',
                        }
                    )
            else:
                await self.send_error("Invalid move")
        except Exception as e:
            await self.send_error(str(e))
                

    #Verifica si la partida ha finalizado con python-chess
    def check_game_end(self):
        return self.board.is_game_over()


    #Envia error
    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    #Desconcexion
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    