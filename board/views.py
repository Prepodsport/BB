from urllib import request
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin

from board.forms import ArticleForm, FeedbackForm, FeedbackFilterForm
from board.models import Article, Feedback
from .tasks import feedback_send_email, feedback_accept_send_email


class ArticleList(ListView):
    """ Представление всех постов в виде списка. """
    paginate_by = 3
    model = Article
    ordering = '-date_time'
    template_name = 'board/articles_list.html'
    context_object_name = 'articles'


class ArticleCreate(LoginRequiredMixin, CreateView):
    """ Представление для создания статьи. """
    raise_exception = True
    form_class = ArticleForm
    model = Article
    template_name = 'board/article_edit.html'
    success_url = reverse_lazy('articles_list')

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Добавить статью"
        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        article.author = User.objects.get(username=str(self.request.user))
        article.save()
        return super().form_valid(form)


class ArticleUpdate(LoginRequiredMixin, UpdateView):
    """ Представление для редактирования статьи. """
    raise_exception = True
    form_class = ArticleForm
    model = Article
    template_name = 'board/article_edit.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Редактировать статью"
        return context


class CommentUpdate(LoginRequiredMixin, UpdateView):
    """ Представление для редактирования комментария. """
    raise_exception = True
    form_class = FeedbackForm
    model = Feedback
    template_name = 'board/comment_edit.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['page_title'] = "Редактировать комментарий"
        return context


""" рабочая форма без подтверждения. """
# def article(request, pk):
#
#    article = Article.objects.get(id=pk)
#    form = FeedbackForm()
#    if request.method == 'POST':
#        form = FeedbackForm(request.POST)
#        feedback = form.save(commit=False)
#        feedback.article = article
#        feedback.author = request.user
#        feedback.save()
#        messages.success(request, 'Ваш отзыв был добавлен!')
#        return redirect(article.get_absolute_url())
#    return render(request, 'board/article_detail.html', {'article': article, 'form': form})

""" рабочая форма с подтверждения. """


# class ArticleDetail(DetailView):
#     """ Представление отдельного поста. """
#     model = Article
#     template_name = 'board/article_detail.html'
#     context_object_name = 'article'
#     slug_field = "url"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["form"] = FeedbackForm()
#         return context
#
#
# class AddFeedback(View):
#     """Отзывы"""
#
#     def post(self, request, pk):
#         form = FeedbackForm(request.POST)
#         article = Article.objects.get(id=pk)
#         if form.is_valid():
#             form = form.save(commit=False)
#             if request.POST.get("parent", None):
#                 form.parent_id = int(request.POST.get("parent"))
#             form.article = article
#             form.author = request.user
#             form.save()
#         return redirect(article.get_absolute_url())

class ArticleDetail(View):

    def get(self, request, *args, **kwargs):
        view = ArticleDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostComment.as_view()
        return view(request, *args, **kwargs)


class FeedbackDisplay(DetailView):
    """ Представление отдельного поста. """
    model = Feedback
    template_name = 'board/article_detail.html'
    context_object_name = 'feedback'


class ArticleDisplay(DetailView):
    """ Представление отдельного поста. """
    model = Article
    template_name = 'board/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FeedbackForm()
        return context


class PostComment(LoginRequiredMixin, FormView):
    model = Article
    form_class = FeedbackForm
    template_name = 'board/article_detail.html'
    comments = Feedback.objects.filter(status=True)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PostComment, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        article = self.get_object()
        return reverse('article_detail', kwargs={'pk': article.pk}) + '#comments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        author_articles = Article.objects.filter(author=user)
        context['author_articles'] = author_articles
        return context


class Search(ListView):
    """Поиск"""
    paginate_by = 3
    model = Article
    context_object_name = 'articles'
    template_name = 'board/articles_list.html'

    def get_queryset(self):
        return Article.objects.filter(text__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context


def comments_detail(request, pk):
    template_name = 'board/article_detail.html'
    article = get_object_or_404(Article, id=pk)
    comments = article.comments.all().filter(status=True)
    new_comment = None
    if request.method == 'POST':
        comment_form = FeedbackForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = Feedback.objects.get(id=parent_id)
                if parent_obj:
                    replay_comment = comment_form.save(commit=False)
                    replay_comment.parent = parent_obj
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.author = request.user
            new_comment.save()
            return HttpResponseRedirect(article.get_absolute_url())
    else:
        comment_form = FeedbackForm()
    return render(request, template_name, {'article': article,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})

    # def get_queryset(self):
    #     queryset = super(Comments, self).get_queryset()
    #     return queryset.filter(status=True)


title = str("")


class FeedbackView(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = 'board/comments.html'
    context_object_name = 'feedbacks'

    def get_context_data(self, **kwargs):
        context = super(FeedbackView, self).get_context_data(**kwargs)
        global title
        """
        Далее в условии - если пользователь попал на страницу через ссылку из письма, в которой содержится
        ID поста для фильтра - фильтр работает по этому ID
        """
        if self.kwargs.get('pk') and Article.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Article.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = FeedbackFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            article_id = Article.objects.get(title=title)
            context['filter_feedback'] = list(Feedback.objects.filter(article_id=article_id).order_by('-created_on'))
            context['feedback_article_id'] = article_id.id
        else:
            context['filter_feedback'] = list(
                Feedback.objects.filter(article_id__author_id=self.request.user).order_by('-created_on'))
        context['my_feedback'] = list(Feedback.objects.filter(author_id=self.request.user).order_by('-created_on'))
        return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')
        """
        Далее в условии - При событии POST (если в пути открытой страницы есть ID) - нужно перезайти уже без этого ID
        чтобы фильтр отрабатывал запрос уже из формы, так как ID, если он есть - приоритетный 
        """
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/board/feedbacks')
        return self.get(request, *args, **kwargs)


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        feedback = Feedback.objects.get(id=kwargs.get('pk'))
        feedback.status = True
        feedback.save()
        feedback_accept_send_email.delay(feedback_id=feedback.id)
        return HttpResponseRedirect('/board/feedbacks')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        feedback = Feedback.objects.get(id=kwargs.get('pk'))
        feedback.delete()
        return HttpResponseRedirect('/board/feedbacks')
    else:
        return HttpResponseRedirect('/accounts/login')
