from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("session/<int:session_id>", views.session, name="session"),
    path("session/<int:session_id>/selectedtimer/<int:timer_id>", views.modify_selected_timer, name="modify_selected_timer"),
    path("get_timer_info/", views.get_timer_info, name="update_timer"),
    path("test/", views.test, name="test"),
]