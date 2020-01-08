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
	if request.method == "POST":
		form = ArticleForm(request.POST)
		if form.is_valid():
			article = form.save(commit=False)
			article.author = request.user
			article.save()
			return redirect('article-details', article.id)

	context = {"form" : form}

	return render(request, "create_article.html", context)