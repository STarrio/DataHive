from django.contrib import admin
from .models import all_models

for model_name, model in all_models.items():
    admin.site.register(model)

