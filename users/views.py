from django.shortcuts import render, reverse, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect

def register(request):
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, 'Account successfully created! Now you can log in!')
      return redirect('index')
  else:
    form = UserCreationForm()
  return render(request, 'users/register.html', {'form':form})
