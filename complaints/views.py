from django.urls import reverse
from .models import Complaint
from institute.models import Student
from django.http.response import Http404
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .forms import MedicalIssueUpdationForm
from complaints.forms import ComplaintUpdationForm
import re

# Create your views here.
class ComplaintDetailView(LoginRequiredMixin, DetailView):
    template_name = 'complaints/show.html'

    def get(self, request, *args, **kwargs):
        response =  super().get(request, *args, **kwargs)
        if self.request.user.is_student and (self.object.entity() != self.request.user.student): 
            raise Http404()
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.object.can_edit(self.request.user)
        if self.model == Complaint:
            context['form'] = ComplaintUpdationForm(instance=self.object)
        else:
            context['form'] = MedicalIssueUpdationForm(instance=self.object)
        return context

class ComplaintCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = 'complaints/new.html'
    
    def get_success_message(self, cleaned_data):
        return '{} created successfully!'.format(self.model.__name__)

    def get_success_url(self):
        return self.request.user.home_url()

    def form_valid(self, form):
        form.instance.user = self.request.user

        if self.model == Complaint:
            form.instance.complainee = form.cleaned_data.get('complainee_id') and Student.objects.get(regd_no = form.cleaned_data.get('complainee_id'))

        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_label = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', self.model.__name__) # CamelCase to Title Case
        context['form_title'] = 'Register {}'.format(model_label)
        context['object_name'] = model_label
        print(context['object_name'])
        return context
    
class ComplaintUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    def get_success_message(self, cleaned_data):
        return '{} updated successfully!'.format(self.get_object().model_name())

    def get_success_url(self):
        # return self.request.user.home_url()
        return reverse('complaints:{}_detail'.format((self.model.__name__).lower()), args=[self.get_object().pk])

class ComplaintDeleteView(LoginRequiredMixin, DeleteView):

    def get_success_url(self):
        return self.request.user.home_url()