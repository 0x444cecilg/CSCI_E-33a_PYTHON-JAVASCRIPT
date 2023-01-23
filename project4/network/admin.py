from django.contrib import admin
from .models import User, Posting, Follow

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username']

class PostingAdmin(admin.ModelAdmin):
    list_display = ['id', 'poster', 'content', 'date']

class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'followee']

admin.site.register(User, UserAdmin)
admin.site.register(Posting, PostingAdmin)
admin.site.register(Follow, FollowAdmin)