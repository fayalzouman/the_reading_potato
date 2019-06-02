from django.urls import path
from main import views 


urlpatterns = [

	path('', views.articles_list, name="articles-list"),
    path('my-articles/', views.my_articles_list, name="my-articles-list"),
    path('articles/<article_slug>/', views.article_details, name="article-details"),
    path('edit/<article_slug>/', views.edit_article, name="edit-article"),
    path('create/', views.create_article, name="create-article"),

	path('contribute/<article_slug>/', views.contribute_to_article, name="contribute-to-article"),
    path('my-contributions/', views.my_contributions_list, name="my-contributions-list"),
	path('contributions/', views.contributions_list, name="contributions-list"),
    path('contributions/<int:contribution_id>/', views.contribution_details, name="contribution-details"),
    path('accept/<int:contribution_id>/', views.accept_changes, name="accept-changes"),
    path('decline/<int:contribution_id>/', views.decline_changes, name="decline-changes"),
]