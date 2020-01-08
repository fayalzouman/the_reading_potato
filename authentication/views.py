from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import UserRegister


def register(request):
	form = UserRegister()
	if request.method == 'POST':
		form = UserRegister(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			login(request, user)
			return redirect("articles-list")
	context = {
        "form":form,
    }
	return render(request, 'register.html', context)