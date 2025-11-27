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

# submenu_items = [
#     MenuItem("Informações", reverse("cms:publication_detail"), icon="bi bi-circle"),
#     MenuItem(
#         "Redes Sociais",
#         reverse("cms:socialmedia_list"),
#         icon="bi bi-circle",
#         check=lambda r: r.user.has_perm("cms.view_socialmedia"),
#     ),
# ]
# Menu.add_item(
#     "cms",
#     MenuItem(
#         "Publicação",
#         "#",
#         icon="bi bi-journals",
#         children=submenu_items,
#         check=lambda r: r.user.has_perm("cms.view_publication"),
#     ),
# )

Menu.add_item(
    "presente",
    MenuItem(
        "Atividades",
        reverse("presente:activity_list"),
        icon="bi bi-list-check",
        check=lambda r: r.user.has_perm("presente.view_activity"),
    ),
)

Menu.add_item(
    "presente",
    MenuItem(
        "Usuários",
        reverse("users:user_list"),
        icon="bi bi-person",
        check=lambda r: r.user.has_perm("users.view_user"),
    ),
)
