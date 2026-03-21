from django import forms
from django.contrib import admin
from rest_framework.authtoken.admin import (
    TokenAdmin,
)  # Don't remove this line! It's weird, but it prevents to register `Auth Token` twice
from rest_framework.authtoken.models import Token, TokenProxy


class TokenForm(forms.ModelForm):
    class Meta:
        model = Token
        fields = ['user']  # Only show the user field, i.e `User*` and hide `Token*`

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.key:
            instance.save()
        return instance


class CustomTokenAdmin(admin.ModelAdmin):
    form = TokenForm
    list_display = ('user', 'key', 'created')
    list_filter = ('created',)
    search_fields = ('user__username', 'user__email', 'key', 'created')
    ordering = ('user',)


class AuthToken(Token):
    class Meta:
        proxy = True
        # Rename `Tokens` label to something else
        verbose_name = 'Auth Token'
        verbose_name_plural = 'Auth Tokens'  # default:r `Tokens`


try:
    admin.site.unregister(TokenProxy)
except admin.sites.NotRegistered:
    pass

# Register the custom TokenAdmin class
admin.site.register(AuthToken, CustomTokenAdmin)
