from djoser.views import TokenCreateView
from djoser.conf import settings

#Añadir user_id y rating a la respuesta ya que djoser no lo ofrece por defecto
class MyTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        respose = super()._action(serializer)
        tokenString = respose.data['auth_token']
        tokenObject = settings.TOKEN_MODEL.objects.get(key=tokenString)
        response.data['user_id'] = tokenObject.user.id
        response.data['rating'] = tokenObject.user.rating
        return response
