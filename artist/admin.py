from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Artists)
class ArtistAdmin(admin.ModelAdmin):
    fieldsets = (('Custom Profile', 
                        {'fields' : 
                        ('user','K_name',"E_name","avatar", "bio_image", "bio_video", "bio_text", "level", "credit"),
                        }
                ),)
    

    list_display = [
        "id",
        "user",
        "K_name",
        "E_name",
        "avatar", 
        "bio_image", 
        "bio_video",
        "bio_text", 
        "level",
        "credit"
    ]

@admin.register(models.Reviews)
class ArtistAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "score",
        "text", 
        "start_date",
    ]    