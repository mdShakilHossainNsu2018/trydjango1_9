from urllib.parse import quote_plus

from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
import os

from django.utils import timezone

from .forms import PostForm
from .models import Post
from django.template import Library, Node, TemplateSyntaxError
from django.core.paginator import Paginator
from django.shortcuts import render


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        # message success
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        "form": form,
    }
    return render(request, "posts/post_form.html", context)


def post_detail(request, slug=None):

    instance = get_object_or_404(Post, slug=slug)
    if instance.publish > timezone.now().date() or instance.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(instance.content)
    context = {
        "title": instance.title,
        "instance": instance,
        "share_string": share_string
    }
    return render(request, "posts/post_detail.html", context)


def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.active()  # .order_by("-timestamp")
    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()

    query = request.GET.get('q')
    if query:
        queryset_list = queryset_list.filter(Q(title__icontains=query) |
                                             Q(content__icontains=query) |
                                             Q(user__first_name__icontains=query) |
                                             Q(user__last_name__icontains=query)).distinct()

    paginator = Paginator(queryset_list, 3)
    page = request.GET.get('page')
    contacts = paginator.get_page(page)
    pagenum = range(contacts.number-2, contacts.number+3)
    context = {
        "object_list": queryset_list,
        "title": "List",
        "contacts": contacts,
        "pagenum": pagenum,
        "today": today,

    }
    return render(request, "posts/post_list.html", context)


def post_update(request, slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form": form,
    }
    return render(request, "posts/post_form.html", context)


def post_delete(request, slug=None):
    if not request.user.is_staff or request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    # Post.objects.get(id=id).image.delete(save=True)
    instance.delete()
    # os.remove(instance.image)
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")


register = Library()


class RangeNode(Node):
    def __init__(self, range_args, context_name):
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):
        context[self.context_name] = range(*self.range_args)
        return ""


@register.tag
def mkrange(parser, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% mkrange [start,] stop[, step] as context_name %}

    For example:
        {% mkrange 5 10 2 as some_range %}
        {% for i in some_range %}
          {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """

    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error():
        raise TemplateSyntaxError("%s accepts the syntax: {%% %s [start,] " + \
                                  "stop[, step] as context_name %%}, where 'start', 'stop' " + \
                                  "and 'step' must all be integers." % (fnctl, fnctl))

    range_args = []
    while True:
        if len(tokens) < 2:
            error()

        token = tokens.pop(0)

        if token == "as":
            break

        if not token.isdigit():
            error()
        range_args.append(int(token))

    if len(tokens) != 1:
        error()

    context_name = tokens.pop()

    return RangeNode(range_args, context_name)
