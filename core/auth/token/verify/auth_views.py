from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

class TokenObtainPairThrottledView(TokenObtainPairView):
    throttle_scope = "auth"

class TokenRefreshThrottledView(TokenRefreshView):
    throttle_scope = "auth"

class TokenVerifyThrottledView(TokenVerifyView):
    throttle_scope = "auth"
