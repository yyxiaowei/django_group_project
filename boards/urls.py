from django.urls import path, include

from . import views

app_name = 'boards'

urlpatterns = [
    # 使用 FBV 时的写法
    # path('', views.view.home, name='home'),
    # path('<int:pk>/', views.board_topics, name='board_topics'),
    # path('<int:pk>/topics/<int:topic_pk>/',views.topic_posts, name='topic_posts'),
    
    # 使用 GCBV 时的写法
    path('', views.BoardListView.as_view(), name='home'),
    path('<int:pk>/', views.TopicListView.as_view(), name='board_topics'),
    path('<int:pk>/topics/<int:topic_pk>/',views.PostListView.as_view(), name='topic_posts'),
    
    path('<int:pk>/new/', views.new_topic, name='new_topic'),
    path('<int:pk>/delete/', views.delete_topic, name='delete_topic'),
    
    path('<int:pk>/topics/<int:topic_pk>/reply/',views.reply_topic, name='reply_topic'),
    path('<int:pk>/topics/<int:topic_pk>/post/<int:post_pk>/',views.PostUpdateView.as_view(), name='edit_post'),
    
]