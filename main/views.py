from django.shortcuts import render, redirect
from .forms import ArticleForm, ContributeArticleForm
from .models import Article, Contribution, Change
import difflib
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import slugify


def articles_list(request):
	articles = Article.objects.all()

	query = request.GET.get("q")
	if query:
		articles = articles.filter(title__contains=query)

	paginator = Paginator(articles, 10) # Show 10 articles per page
	page_number = request.GET.get('page')

	try:
		objects = paginator.page(page_number)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		objects = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		objects = paginator.page(paginator.num_pages)

	context = {
		"articles" : objects,
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

def my_contributions_list(request):
	if request.user.is_anonymous:
		return redirect('login')

	return render(request, "my_contributions_list.html")

def contributions_list(request):
	if request.user.is_anonymous:
		return redirect('articles-list')

	contributions = Contribution.objects.filter(status=Contribution.PENDING, article__author=request.user)
	context = {"contributions" : contributions}
	return render(request, 'contributions_list.html', context)

def contribute_to_article(request, article_id):
	if request.user.is_anonymous:
		return redirect('login')
		
	article = Article.objects.get(id=article_id)
	
	#the author shouldn't be able to contribute, they can only edit
	if article.author == request.user:
		return redirect('edit-article', article_id)

	form = ContributeArticleForm(instance=article)
	if request.method == "POST":
		form = ContributeArticleForm(request.POST)

		if form.is_valid():
			changed_article = form.save(commit=False)
			contribution = Contribution.objects.create(user=request.user, article=article)
			Change.objects.create(new_content=changed_article.content, contribution=contribution)
			return redirect('my-contributions-list')

	context = {"form":form, "article":article}
	return render(request, 'contribute_to_article.html', context)

def contribution_details(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)
	if request.user != contribution.article.author:
		return redirect('articles-list')

	d = difflib.Differ()
	comparison = list(d.compare(contribution.article.content.splitlines(True), contribution.change.new_content.splitlines(True)))


	context = {
		"contribution" : contribution,
		"comparison" : comparison,
	}
	
	return render(request, 'contribution_details.html', context)

def accept_changes(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)

	if request.user != contribution.article.author:
		return redirect('articles-list')

	
	contribution.status = Contribution.ACCEPTED
	contribution.save()

	article = contribution.article
	article.content = contribution.change.new_content
	article.save()

	contribution.change.delete()

	return redirect('contributions-list')

def decline_changes(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)

	if request.user != contribution.article.author :
		return redirect('articles-list')

	contribution.status = Contribution.DECLINED
	contribution.save()

	contribution.change.delete()

	return redirect('contributions-list')


# def article_details(request, article_id):
# 	article = Article.objects.get(id=article_id)
# 	if settings.DEBUG:
# 		contributions = article.contributions.filter(status=Contribution.ACCEPTED)
# 	else:
# 		contributions = article.contributions.filter(status=Contribution.ACCEPTED).distinct('user')

# 	context = {
# 		"article": article,
# 		"contributions": contributions,
# 		}
# 	return render(request, "article_details.html", context)

def article_details(request, article_slug):
    context = { "article" : Article.objects.get(slug=article_slug)}
    return render(request, 'article_details.html', context)
