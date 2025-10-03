from django.contrib import admin
from .models import User, DashboardStats

# Como os modelos não são gerenciados pelo Django (managed=False),
# não registraremos no admin por enquanto.
# Futuramente, pode ser útil para debug.

# admin.site.register(User)
# admin.site.register(DashboardStats)