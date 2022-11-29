from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

class RolInline(admin.StackedInline):
    model = RolDeUsuario
    can_delete = False
    verbose_name_plural = 'Tipos de usuarios'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (RolInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(RegistroDeUsuarios)
admin.site.register(User, UserAdmin)
admin.site.register(Userip)
admin.site.register(VisitNumber)
admin.site.register(DayNumber)
admin.site.register(RegistroTotalDeIngresos)
admin.site.register(TotalGeneralDeIngresos)
admin.site.register(ComisionesDeStaff)
admin.site.register(Mensajes)
