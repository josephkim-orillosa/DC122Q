from django.contrib import admin

from .models import AccountProfile, Event, Student


admin.site.register(AccountProfile)
admin.site.register(Student)
admin.site.register(Event)
