from celery import current_app as app

from .marketplace_user_perms import AddMarketplaceUserPermsTask, RemoveMarketplaceUserPermsTask

app.tasks.register(AddMarketplaceUserPermsTask())
app.tasks.register(RemoveMarketplaceUserPermsTask())
