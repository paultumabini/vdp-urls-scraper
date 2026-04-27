from django import forms
from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin  # noqa: F401
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
        verbose_name = 'Auth Token'
        verbose_name_plural = 'Auth Tokens'


try:
    admin.site.unregister(TokenProxy)
except admin.sites.NotRegistered:
    pass

admin.site.register(AuthToken, CustomTokenAdmin)
