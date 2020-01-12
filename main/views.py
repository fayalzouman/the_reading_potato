from django.shortcuts import render, redirect
from .models import Article
from .forms import ArticleForm

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

def create_article(request):
	form = ArticleForm()
	if request.user.is_anonymous:
		return redirect('login')
	if request.method == "POST":
		form = ArticleForm(request.POST)
		if form.is_valid():
			article = form.save(commit=False)
			article.author = request.user
			article.save()
			return redirect('article-details', article.id)

	context = {"form" : form}

	return render(request, "create_article.html", context)

def edit_article(request, article_id):
	
	article = Article.objects.get(id=article_id)
	form = ArticleForm(instance=article)
	if article.author != request.user:
		return redirect('article-details', article_id)

	if request.method == "POST":
		form = ArticleForm(request.POST, instance=article)

		if form.is_valid():
			form.save()
			return redirect('article-details', article_id)

	context = {"form":form, "article":article}
	return render(request, 'edit_article.html', context)

def my_articles_list(request):
	return render(request, "my_articles_list.html")