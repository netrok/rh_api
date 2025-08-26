# core/jwt.py
from typing import Any, Dict
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        """
        Agrega claims personalizados al REFRESH token.
        El ACCESS token que devuelve SimpleJWT hereda estos claims.
        """
        token = super().get_token(user)  # ya contiene "user_id"
        token["username"] = user.get_username() or ""
        token["email"] = getattr(user, "email", "") or ""
        token["is_staff"] = bool(getattr(user, "is_staff", False))
        token["is_superuser"] = bool(getattr(user, "is_superuser", False))
        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        OPCIONAL: agrega info del usuario en el body de la respuesta del login,
        junto con access/refresh.
        """
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": user.id,
            "username": user.get_username(),
            "email": getattr(user, "email", ""),
            "is_staff": bool(getattr(user, "is_staff", False)),
            "is_superuser": bool(getattr(user, "is_superuser", False)),
        }
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
