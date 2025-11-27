from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return settings.OPEN_FOR_SIGNUP or False


class SuapSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        # Extra data in: sociallogin.account.extra_data
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        # Basic user fields
        user_email(user, data.get("email") or "")
        user_field(user, "first_name", data.get("first_name"))
        user_field(user, "last_name", data.get("last_name"))

        # Full name - respect nome_social if available
        nome_completo = extra_data.get("nome_registro", "")
        if nome_social := extra_data.get("nome_social"):
            nome_completo = nome_social
        if nome_completo:
            user.full_name = nome_completo

        # User type from tipo_usuario
        tipo_usuario = extra_data.get("tipo_usuario", "")
        if "Servidor" in tipo_usuario:
            user.type = "SERVIDOR"
        elif "Aluno" in tipo_usuario:
            user.type = "ALUNO"

        # Avatar URL from foto
        foto = extra_data.get("foto")
        if foto:
            user.avatar_url = foto

        # Mark as SUAP user
        user.is_suap_user = True

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Override to update user data on every login, not just on signup.
        """
        user = super().save_user(request, sociallogin, form)

        # Update user data from SUAP on every login
        extra_data = sociallogin.account.extra_data

        # Update basic fields
        user.first_name = extra_data.get("primeiro_nome", "")
        user.last_name = extra_data.get("ultimo_nome", "")

        # Update full name - respect nome_social if available
        nome_completo = extra_data.get("nome_registro", "")
        if nome_social := extra_data.get("nome_social"):
            nome_completo = nome_social
        if nome_completo:
            user.full_name = nome_completo

        # Update user type
        tipo_usuario = extra_data.get("tipo_usuario", "")
        if "Servidor" in tipo_usuario:
            user.type = "SERVIDOR"
        elif "Aluno" in tipo_usuario:
            user.type = "ALUNO"

        # Update avatar URL
        foto = extra_data.get("foto")
        if foto:
            user.avatar_url = foto

        # Mark as SUAP user
        user.is_suap_user = True

        user.save()
        return user

    def is_open_for_signup(self, request, sociallogin):
        return settings.OPEN_FOR_SIGNUP or False
