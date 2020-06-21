from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post

# 使用 FBV 时的写法
def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1) # 获取url中page参数,初始获取第一页
    paginator = Paginator(queryset, 20) # 设置每页显示20条数据
    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码不是数字则返回第一页
        topics = paginator.page(1)
    except EmptyPage:
        # 页码输入查询为空，返回最后一页
        topics = paginator.page(paginator.num_pages)
    return render(request, 'boards/topics.html', {'board': board, 'topics': topics})

def topic_posts(request,pk,topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'boards/topic_posts.html', {'topic': topic})

# 使用 GCBV时的写法
class BoardListView(generic.ListView):
    context_object_name = 'boards'
    template_name = 'boards/home.html'
    
    def get_queryset(self):
        return Board.objects.all()


class TopicListView(generic.ListView):
    model = Topic
    template_name = 'boards/topics.html'
    context_object_name = 'topics'
    # 设置分页属性 每页显示20条  
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)
    
    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


class PostListView(generic.ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'boards/topic_posts.html'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        # session控制post页面刷新次数
        session_key = f'viewed_topic_{self.topic.pk}'
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        # 存储post分页至edit post页面 
        self.request.session['post_cur_page'] = self.request.GET.get('page',1)
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)
    
    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

# 页面div指定id,定位到更新后的topic
def redirect_to_topic_posts(pk,topic_pk,post_pk,page_num):
    topic_url = reverse('boards:topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
    topic_post_url = f'{topic_url}?page={page_num}#{post_pk}'
    return topic_post_url


@method_decorator(login_required, name='dispatch')
class PostUpdateView(generic.UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'boards/edit_post.html'
    pk_url_kwarg = 'post_pk'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.update_by = self.request.user
        post.update_at = timezone.now()
        post.save()
        post_cur_page = self.request.session.get('post_cur_page',1)
        topic_post_url = redirect_to_topic_posts(
            post.topic.board.pk,
            post.topic.pk,
            post.pk,
            post_cur_page
        )
        return redirect(topic_post_url)


@login_required
def reply_topic(request,pk,topic_pk):
    topic = get_object_or_404(Topic, board_id=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            topic.last_updated = timezone.now()
            topic.save()
            topic_post_url = redirect_to_topic_posts(pk,topic_pk,post.pk,topic.get_page_count())
            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request,'boards/reply_topic.html', {'form': form, 'topic': topic })


@login_required
def new_topic(request,pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message= form.cleaned_data.get('message'),
                topic= topic,
                created_by= request.user
            )
            return redirect('boards:topic_posts', pk=pk, topic_pk= topic.pk)
    else:
        form = NewTopicForm()
    return render(request, 'boards/new_topic.html', { 'form': form, 'board': board })


@login_required
def delete_topic(request,pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form_list = request.POST.getlist('topic_id')
        for f in form_list:
            topic = Topic.objects.get(id=f)
            topic.delete()
    return redirect('boards:board_topics', pk=board.pk)
    

