from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.checks.messages import Error
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, Follow

User = get_user_model()


def index(request):
    post_list = Post.objects.all()
    title = "Последние обновления на сайте"
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "title": title,
        "post_list": post_list,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    title = group.title
    description = group.description
    context = {
        "page_obj": page_obj,
        "title": title,
        "description": description,
        "post_list": post_list,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    author_name = username
    post_all = Post.objects.filter(author=author).count()
    paginator = Paginator(post_list, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if request.user.is_anonymous:
        following = False
    else:
        try:
            Follow.objects.get(user=request.user, author=author)
        except Follow.DoesNotExist:
            following = False
        else:
            following = True

    context = {
        "page_obj": page_obj,
        "post_list": post_list,
        "post_all": post_all,
        "author_name": author_name,
        "author": author,
        "following": following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    post_list = Post.objects.all()
    post_all = Post.objects.filter(author=author).count()
    form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    context = {
        "post": post,
        "post_all": post_all,
        "post_list": post_list,
        "comments": comments,
        "form": form,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=request.user.username)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id=pk)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=pk)
    context = {
        "post": post,
        "form": form,
        "is_edit": True,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    posts = Post.objects.filter(author__following__user=request.user)
    title = "Посты на которые вы подписаны"
    paginator = Paginator(posts, settings.DEFAULT_POSTS_ON_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "title": title,
    }
    return render(request, "posts/follow.html", context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    follow_obj = Follow.objects.get(user=request.user, author=author)
    follow_obj.delete()
    return redirect("posts:profile", username)
