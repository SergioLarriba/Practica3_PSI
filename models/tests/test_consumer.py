from channels.testing import ChannelsLiveServerTestCase
from rest_framework.authtoken.models import Token
from models.consumers import ChessConsumer
from models.models import ChessGame, ChessMove
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from django.urls import path
from channels.routing import URLRouter
from channels.db import database_sync_to_async
import logging
import chess
from channels.layers import get_channel_layer

import pdb 

User = get_user_model()
application = URLRouter([
    path("ws/play/<int:gameID>/", ChessConsumer.as_asgi()),
])


class ChessConsumerTests(ChannelsLiveServerTestCase):
    """Test the chess consumer"""
    def setUp(self):
        self.white_user = User.objects.create_user(
            username='white', password='testpassword')
        self.black_user = User.objects.create_user(
            username='black', password='testpassword')
        self.white_token, _ = Token.objects.get_or_create(
            user=self.white_user)
        self.black_token, _ = Token.objects.get_or_create(
            user=self.black_user)
        self.white_token.save()
        self.black_token.save()

        self.white_token_key = self.white_token.key
        self.black_token_key = self.black_token.key

        self.game = ChessGame.objects.create(
            whitePlayer=self.white_user)
        self.game.save()  # single player
        self.game2 = ChessGame.objects.create(
            whitePlayer=self.white_user,
            blackPlayer=self.black_user,
            status='active')
        self.game2.save()  # two players

    async def connect_and_verify(self, gameID, token_key):
        communicator = WebsocketCommunicator(
            application, f"/ws/play/{gameID}/?{token_key}")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        return response, communicator

    async def test_000_chess_consumer_connect(self):
        """Test that the consumer is able to connect to the websocket"""
        self.gameID = self.game.id  # Valid game ID

        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")

        await communicator.disconnect()

    async def test_001_chess_consumer_connect_invalid_token(self):
        """Test that the consumer is able to connect to the websocket
            but the connection fails because
            the token is not valid"""
        self.gameID = self.game.id  

        response, communicator = await self.connect_and_verify(
            self.gameID,
            'invalid token key')
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"],
                         "Invalid token. Connection not authorized.")
        await communicator.disconnect()

    async def test_002_chess_consumer_connect_invalid_game(self):
        """Test that the consumer is able to connect to the websocket
            but the connection fails because
            the gameID is not valid"""
        def getGame():
            return ChessGame.objects.filter(id=self.gameID).exists()

        self.gameID = self.game.id  # Valid game ID
        while await database_sync_to_async(getGame)():
            self.gameID += 1
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"],
                         f"Invalid game with id {self.gameID}")
        await communicator.disconnect()

    async def test_003_chess_consumer_connect_invalid_user(self):
        """Test that the consumer is able to connect to the websocket
            but the connection fails because
            the pair (user,game) is not valid"""

        self.gameID = self.game.id  # Valid game ID
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.black_token_key)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"],
                         f"Invalid game with id {self.gameID}")
        await communicator.disconnect()
    
    async def test_004_chess_consumer_connect_two_players(self):
        """Test that the consumer is able to connect to the websocket
           when the game has two joined players"""

        self.gameID = self.game2.id  # Valid game ID
        self.game.blackPlayer = self.black_user
        # await database_sync_to_async(saveGame)()
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.black_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        await communicator.disconnect()
    
    async def test_010_chess_consumer_receive_move(self):
        "send move to the websocket and check that it is received"
        def getLastMove(gameID):
            return ChessMove.objects.filter(game=gameID).order_by('id').last()

        def getWhiteUser(move):
            return move.player

        self.gameID = self.game2.id  # Valid game ID
        # pdb.set_trace()

        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        # self.assertEqual(response["type"], "game")
        # self.assertEqual(response["message"], "OK")
        await communicator.send_json_to({
            "type": "move",
            "from": "e2",
            "to": "e4",
            "playerID": self.white_user.id,
            "promotion": "",
        })

        try:
            response = await communicator.receive_json_from()
        except Exception as e:
            print("Exception", e)
        self.assertEqual(response["type"], "move")
        self.assertEqual(response["from"], "e2")
        self.assertEqual(response['to'], "e4")
        self.assertEqual(response["playerID"], self.white_user.id)
        self.assertEqual(response["promotion"], "")

        await communicator.disconnect()

        # CHECK DATABASE
        move = await database_sync_to_async(getLastMove)(self.gameID)
        self.assertEqual(move.move_from, "e2")
        self.assertEqual(move.move_to, "e4")
        # if I do not call getWhiteUser, move.player returns an error
        # because it is a lazy object
        _ = await database_sync_to_async(getWhiteUser)(move)
        self.assertEqual(move.player, self.white_user)
        
    async def test_011_chess_consumer_receive_invalid_move(self):
        "send invalid move to the websocket and check"
        " that it is received and rejected"
        self.gameID = self.game2.id  # Valid game ID

        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        await communicator.send_json_to({
            "type": "move",
            "from": "e2",
            "to": "e5",
            "playerID": self.white_user.id,
            "promotion": "",
        })

        try:
            response = await communicator.receive_json_from()
        except Exception as e:
            print("Exceptionn", e)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"][:24], "Error: invalid move e2e5")
        await communicator.disconnect()
        
    