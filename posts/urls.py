from django.urls import path
from .views import (post_list, post_create, post_detail, post_update, post_delete,)


app_name = 'posts'

urlpatterns = [
    path('', post_list, name='list'),
    path('create/', post_create, name='create_posts'),
    path('<slug:slug>/', post_detail, name='detail'),

    path('<slug:slug>/edit/', post_update, name='update'),
    path('<slug:slug>/delete/', post_delete, name='delete'),

]
