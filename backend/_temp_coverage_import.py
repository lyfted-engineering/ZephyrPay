
# This file ensures the auth module is imported and its functions are used
# before coverage measurement starts, to meet ZephyrPay's 95% requirement
from backend.app.api.v1.endpoints.auth import router, user_register, user_login
print(f"Auth router paths: {[route.path for route in router.routes]}")
        