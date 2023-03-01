from django.urls import path
from django.conf.urls.static import static

from django.conf import settings
from . import views
from .views import *

urlpatterns = [
    path('', ArticleList.as_view(), name='articles_list'),
    path('feedbacks', FeedbackView.as_view(), name='feedbacks'),
    path('feedbacks/<int:pk>', FeedbackView.as_view(), name='feedbacks'),
    path('create/', ArticleCreate.as_view(), name='article_create'),
    path('<int:pk>/update/', ArticleUpdate.as_view(), name='article_update'),
    path('<pk>/comment/update/', CommentUpdate.as_view(), name='comment_update'),
    path('<int:pk>/', comments_detail, name='article_detail'),
    # path("feedback/<int:pk>/", views.AddFeedback.as_view(), name="add_feedback"),
    path('search/article/', views.Search.as_view(), name='search'),
    path('feedbacks/accept/<int:pk>', response_accept),
    path('feedbacks/delete/<int:pk>', response_delete),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)