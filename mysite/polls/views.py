from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone


from .models import Question, Choice
from .forms import CustomUserCreationForm, CreatePollFormSet


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those
        to be published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class MyPollsView(LoginRequiredMixin, generic.ListView):
    template_name = 'polls/mypolls.html'
    context_object_name = "question_list"

    def get_queryset(self):
        """
        Return the list of all polls owned by logged in user.
        """
        return Question.objects.filter(
            owner=self.request.user.id
        ).order_by('-pub_date')


class SearchView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'polls/search.html'
    model = Question

    def get_context_data(self, *args, **kwargs):
        context = super(SearchView, self).get_context_data(*args, **kwargs)
        question_text = self.request.GET.get('q', '')

        if question_text != '':
            question_list = self.model.objects.filter(
                question_text__icontains=question_text)
            context['q'] = question_text
        else:
            question_list = self.model.objects.all()

        context['question_list'] = question_list
        return context


class CreatePollView(LoginRequiredMixin, generic.CreateView):
    model = Question
    fields = ['question_text']
    success_url = reverse_lazy('polls:mypolls')
    template_name = 'polls/create_poll.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_owner'] = True
        if self.request.POST:
            context['choices'] = CreatePollFormSet(self.request.POST)
        else:
            context['choices'] = CreatePollFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choices = context['choices']
        form.instance.owner = self.request.user
        with transaction.atomic():
            self.object = form.save()

            if choices.is_valid():
                choices.instance = self.object
                choices.save()
        # why do we need to use super(...) instead of super()
        return super(CreatePollView, self).form_valid(form)


class UpdatePollView(LoginRequiredMixin, generic.UpdateView):
    model = Question
    fields = ['question_text', 'owner']
    success_url = reverse_lazy('polls:mypolls')
    template_name = 'polls/create_poll.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.owner == self.request.user:
            context['is_owner'] = True

            if self.request.POST:
                context['choices'] = CreatePollFormSet(
                    self.request.POST, instance=self.object)
            else:
                context['choices'] = CreatePollFormSet(instance=self.object)
        else:
            context['is_owner'] = False
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choices = context['choices']
        with transaction.atomic():
            self.object = form.save()

            if choices.is_valid():
                choices.instance = self.object
                choices.save()
        return super(UpdatePollView, self).form_valid(form)


class DeletePollView(LoginRequiredMixin, generic.DeleteView):
    model = Question
    success_url = reverse_lazy('polls:mypolls')
    template_name = 'polls/confirm_delete.html'

    # there should be another way to do it (and show message or return HttpResponseForbidden)
    # def get_queryset(self):
    #     owner = self.request.user
    #     return self.model.objects.filter(owner=owner)

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super().get_object()
        if not obj.owner == self.request.user:
            raise PermissionDenied
        return obj


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(LoginRequiredMixin, generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super().get_object()
        if not obj.owner == self.request.user:
            raise PermissionDenied
        return obj


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
