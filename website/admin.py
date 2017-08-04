from django.contrib import admin

from .models import *


# Register your models here.
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = ('name', )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', )
    readonly_fields = ('name', )


@admin.register(Binary)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('problem', 'hash', )
    readonly_fields = ('problem', 'hash', )


@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'team', 'timestamp', 'binary', )
    readonly_fields = ('id', 'team', 'binary', )


@admin.register(AttackLog)
class AttackLogAdmin(admin.ModelAdmin):
    list_display = ('team', 'problem', 'timestamp', )
    readonly_fields = ('team', 'problem', 'timestamp', )