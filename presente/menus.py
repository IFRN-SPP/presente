from django.urls import reverse
from simple_menu import Menu, MenuItem

Menu.add_item(
    "presente",
    MenuItem(
        "Início",
        reverse("presente:index"),
        icon="bi bi-house-fill",
        exact_url=reverse("presente:index"),
    ),
)

Menu.add_item(
    "presente",
    MenuItem(
        "Minhas Presenças",
        reverse("presente:my_attendances"),
        icon="bi bi-check2-circle",
    ),
)

Menu.add_item(
    "presente",
    MenuItem(
        "Minhas Atividades",
        reverse("presente:activity_list"),
        icon="bi bi-list-check",
        check=lambda r: r.user.has_perm("presente.view_activity"),
    ),
)

# ADMINISTRAÇÃO section starts here (items below appear under "ADMINISTRAÇÃO" header)

Menu.add_item(
    "presente",
    MenuItem(
        "Atividades",
        reverse("presente:admin_activities"),
        icon="bi bi-list-check",
        check=lambda r: r.user.is_superuser,
    ),
)

Menu.add_item(
    "presente",
    MenuItem(
        "Usuários",
        reverse("users:user_list"),
        icon="bi bi-person",
        check=lambda r: r.user.is_superuser,
    ),
)

Menu.add_item(
    "presente",
    MenuItem(
        "Redes",
        reverse("presente:network_list"),
        icon="bi bi-hdd-network",
        check=lambda r: r.user.is_superuser,
    ),
)
