from django.test import TestCase

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter

from django.urls import path
from models.consumers import Consumer

application = URLRouter([
	path('ws/chat/<room_name>/', Consumer.as_asgi()),
])

class ChatTests1(TestCase):
	""" 
 	Opens a connection to the consumer, 
	sends a message, and checks that the message is received.  
	"""
	async def test_chat(self):
		# Navegador virtual que se puede conectar a los 2 sockets 
		communicator = WebsocketCommunicator(application, "/ws/chat/room_name/")
	
		# Connect to the consumer 
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
	
		# Send a message to the consumer 
		await communicator.send_json_to({
			'message': "Hello, World!"
		})
  
		# Receive a message from the consumer 
		response = await communicator.receive_json_from()
  
		# Check the message 
		self.assertEqual(response['message'], "Hello, World!")
  
		# Disconnect from the consumer
		await communicator.disconnect()
  
class ChatTest2(TestCase): 
  """ 
  Open two connections to the consumer, 
  send a message from one and check that the message is received by both
  """
  async def test_chat(self):
    communicator1 = WebsocketCommunicator(application, "/ws/chat/room_name/")
    communicator2 = WebsocketCommunicator(application, "/ws/chat/room_name/")
    
    # Connect comunicator 1 
    connected1, _ = await communicator1.connect()
    self.assertTrue(connected1)
    
    # Connect comunicator 2
    connected2, _ = await communicator2.connect()
    self.assertTrue(connected2)
    
    # Comunicator 1 sends a message 
    await communicator1.send_json_to({
			'message': "Hello, comunicator2!"
		})
    
    # Both comunicators receive the message
    response1 = await communicator1.receive_json_from()
    response2 = await communicator2.receive_json_from()
    
    self.assertEqual(response1['message'], "Hello, comunicator2!")
    self.assertEqual(response2['message'], "Hello, comunicator2!")
    
    # Disconnect both communicators 
    await communicator1.disconnect()
    await communicator2.disconnect()
    