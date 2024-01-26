from django.urls import path

from .views import NotificationView, unset_active_for_all, unset_active

app_name = "notification"
urlpatterns = [
    path('notifications/', NotificationView.as_view()),
    path('unset_notifications/', unset_active_for_all),
    path('unset_notification/<int:notificationId>', unset_active),
]
