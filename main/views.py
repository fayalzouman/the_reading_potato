from django.shortcuts import render, redirect
from .models import Article
# from django.contrib.auth import login, authenticate, logout

def articles_list(request):
    articles = Article.objects.all()
    print(articles)
    context = {
        "articles" : articles,
    }
    return render(request, "articles_list.html", context)

def article_details(request, article_id):
    context = { 
        "article" : Article.objects.get(id=article_id)
        }
    return render(request, 'article_details.html', context)