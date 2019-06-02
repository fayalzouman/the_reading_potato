from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

import difflib

from .models import Article, Contribution, Change
from .forms import ArticleForm, ContributeArticleForm


def articles_list(request):
	q = ''
	if request.GET.get('q'):
		q = request.GET.get('q')

	articles = Article.objects.filter(title__icontains=q).order_by("-created_on")

	paginator = Paginator(articles, 10) 
	page_number = request.GET.get('page')

	try:
		objects = paginator.page(page_number)
	except PageNotAnInteger:
		objects = paginator.page(1)
	except EmptyPage:
		objects = paginator.page(paginator.num_pages)

	
	context = {"articles" : objects}
	return render(request, 'articles_list.html',context)


def article_details(request, article_slug):
	article = Article.objects.get(slug=article_slug)
	if settings.DEBUG:
		contributions = article.contributions.filter(status=Contribution.ACCEPTED)
	else:
		contributions = article.contributions.filter(status=Contribution.ACCEPTED).distinct('user')

	context = {
		"article": article,
		"contributions": contributions,
		}
	return render(request, "article_details.html", context)


def my_articles_list(request):
	if request.user.is_anonymous:
		return redirect('login')

	return render(request, "my_articles_list.html")


def create_article(request):
	if request.user.is_anonymous:
		return redirect('login')

	form = ArticleForm()
	if request.method == "POST":
		form = ArticleForm(request.POST)
		if form.is_valid():
			article = form.save(commit=False)
			article.author = request.user
			article.save()

			return redirect('article-details', article.slug)

	context = {"form" : form}

	return render(request, "create_article.html", context)


def edit_article(request, article_slug):
	article = Article.objects.get(slug=article_slug)

	form = ArticleForm(instance=article)
	if request.method == "POST":
		form = ArticleForm(request.POST, instance=article)

		if form.is_valid():
			form.save()
			return redirect('article-details', article_slug)

	context = {"form":form, "article":article}
	return render(request, 'edit_article.html', context)


def contribute_to_article(request, article_slug):
	if request.user.is_anonymous:
		return redirect('login')
		
	article = Article.objects.get(slug=article_slug)
	
	#the author shouldn't be able to contribute, they can only edit
	if article.author == request.user:
		return redirect('edit-article', article_slug)

	form = ContributeArticleForm(instance=article)
	if request.method == "POST":
		form = ContributeArticleForm(request.POST)

		if form.is_valid():
			changed_article = form.save(commit=False)
			contribution = Contribution.objects.create(user=request.user, article=article)
			Change.objects.create(new_content=changed_article.content, contribution=contribution)
			return redirect('contributions-list')

	context = {"form":form, "article":article}
	return render(request, 'contribute_to_article.html', context)


def my_contributions_list(request):
	if request.user.is_anonymous:
		return redirect('login')

	return render(request, "my_contributions_list.html")


def contributions_list(request):
	if request.user.is_anonymous:
		return redirect('pages-list')

	contributions = Contribution.objects.filter(status=Contribution.PENDING, article__author=request.user)
	context = {"contributions" : contributions}
	return render(request, 'contributions_list.html', context)


def contribution_details(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)
	if not( request.user.is_authenticated or request.user == contribution.article.author):
		return redirect('articles-list')

	d = difflib.Differ()
	comparison = list(d.compare(contribution.article.content.splitlines(1), contribution.change.new_content.splitlines(1)))


	context = {
		"contribution" : contribution,
		"comparison" : comparison,
	}
	
	return render(request, 'contribution_details.html', context)


def accept_changes(request, contribution_id):
	contribution = Contribution.objects.get(id=contribution_id)

	if not( request.user.is_authenticated or request.user == contribution.article.author) :
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

	if not( request.user.is_authenticated or request.user == contribution.article.author) :
		return redirect('articles-list')

	contribution.status = Contribution.DECLINED
	contribution.save()

	contribution.change.delete()

	return redirect('contributions-list')