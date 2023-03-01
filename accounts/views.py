from django.contrib.auth.models import Group
from django.http import HttpResponse
from board.models import Article
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from .models import Profile


def register(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST, instance=request.user)
        profile = Profile.objects.get(user=request.user)
        if user_form.is_valid():
            user_form.save()
            return HttpResponse('теперь вы зарегистрированы')
    else:
        user_form = SignUpForm(instance=request.user)
        profile = Profile.objects.get(user=request.user)
    return render(request, 'account/signup.html', {
        'user_form': user_form,

    })


class ProfileView(DetailView):
    model = Profile
    template_name = 'accounts/profile.html'

    def get_context_data(self, *args, **kwargs):
        user = Profile.objects.all()
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        page_user = get_object_or_404(Profile, id=self.kwargs['pk'])
        context['page_user'] = page_user
        return context





