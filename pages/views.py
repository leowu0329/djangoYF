from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import Cases, Land, Build, Person, Survey, FinalDecision, Result, ObjectBuild
from .forms import CasesForm, LandForm, BuildForm, PersonForm, SurveyForm, FinalDecisionForm, ResultForm, ObjectBuildForm

@login_required  # 這個裝飾器會自動檢查登入狀態
def home_page(request):
    return render(request, 'home.html')  # 假設你的首頁模板是 home.html

class CaseListView(LoginRequiredMixin, ListView):
    model = Cases
    template_name = 'cases/case_list.html'  # <app>/<model>_list.html
    context_object_name = 'cases'
    ordering = ['timestamp']

class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Cases
    template_name = 'cases/case_detail.html'
    context_object_name = 'case'

class CaseCreateView(LoginRequiredMixin, CreateView):
    model = Cases
    template_name = 'cases/case_form.html'
    form_class = CasesForm

    @xframe_options_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('is_iframe'):
            context['is_modal_form'] = True
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"案件 '{form.instance.caseNumber}' 建立成功！")
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.GET.get('is_iframe'):
            return render(self.request, 'cases/case_form_success.html', {'case_id': form.instance.id})
        return response

class CaseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Cases
    template_name = 'cases/case_form.html'
    form_class = CasesForm

    @xframe_options_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('is_iframe'):
            context['is_modal_form'] = True
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"案件 '{form.instance.caseNumber}' 更新成功！")
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest' or self.request.GET.get('is_iframe'):
            return render(self.request, 'cases/case_form_success.html', {'case_id': form.instance.id})
        return response

    def test_func(self):
        case = self.get_object()
        if self.request.user == case.user:
            return True
        return False

class CaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Cases
    template_name = 'cases/case_confirm_delete.html'
    context_object_name = 'case'
    success_url = reverse_lazy('case_list')

    def test_func(self):
        case = self.get_object()
        if self.request.user == case.user:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        case = self.get_object()
        messages.success(self.request, f"案件 '{case.caseNumber}' 已成功刪除！")
        return super().delete(request, *args, **kwargs)

# Land CRUD
class LandCreateView(LoginRequiredMixin, CreateView):
    model = Land
    form_class = LandForm
    template_name = 'lands/land_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "土地資料已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class LandUpdateView(LoginRequiredMixin, UpdateView):
    model = Land
    form_class = LandForm
    template_name = 'lands/land_form.html'

    def form_valid(self, form):
        messages.success(self.request, "土地資料已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class LandDeleteView(LoginRequiredMixin, DeleteView):
    model = Land
    template_name = 'lands/land_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "土地資料已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

# Build CRUD
class BuildCreateView(LoginRequiredMixin, CreateView):
    model = Build
    form_class = BuildForm
    template_name = 'builds/build_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "建物資料已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class BuildUpdateView(LoginRequiredMixin, UpdateView):
    model = Build
    form_class = BuildForm
    template_name = 'builds/build_form.html'

    def form_valid(self, form):
        messages.success(self.request, "建物資料已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class BuildDeleteView(LoginRequiredMixin, DeleteView):
    model = Build
    template_name = 'builds/build_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "建物資料已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

# Person CRUD
class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = 'people/person_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "人員資料已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = 'people/person_form.html'

    def form_valid(self, form):
        messages.success(self.request, "人員資料已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class PersonDeleteView(LoginRequiredMixin, DeleteView):
    model = Person
    template_name = 'people/person_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "人員資料已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

# Survey CRUD
class SurveyCreateView(LoginRequiredMixin, CreateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "勘查資料已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'

    def form_valid(self, form):
        messages.success(self.request, "勘查資料已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class SurveyDeleteView(LoginRequiredMixin, DeleteView):
    model = Survey
    template_name = 'surveys/survey_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "勘查資料已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

# FinalDecision CRUD
class FinalDecisionCreateView(LoginRequiredMixin, CreateView):
    model = FinalDecision
    form_class = FinalDecisionForm
    template_name = 'finaldecisions/finaldecision_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "最終判定已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class FinalDecisionUpdateView(LoginRequiredMixin, UpdateView):
    model = FinalDecision
    form_class = FinalDecisionForm
    template_name = 'finaldecisions/finaldecision_form.html'

    def form_valid(self, form):
        messages.success(self.request, "最終判定已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class FinalDecisionDeleteView(LoginRequiredMixin, DeleteView):
    model = FinalDecision
    template_name = 'finaldecisions/finaldecision_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "最終判定已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

# Result CRUD
class ResultCreateView(LoginRequiredMixin, CreateView):
    model = Result
    form_class = ResultForm
    template_name = 'results/result_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "結果資料已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class ResultUpdateView(LoginRequiredMixin, UpdateView):
    model = Result
    form_class = ResultForm
    template_name = 'results/result_form.html'

    def form_valid(self, form):
        messages.success(self.request, "結果資料已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class ResultDeleteView(LoginRequiredMixin, DeleteView):
    model = Result
    template_name = 'results/result_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "結果資料已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

# ObjectBuild CRUD
class ObjectBuildCreateView(LoginRequiredMixin, CreateView):
    model = ObjectBuild
    form_class = ObjectBuildForm
    template_name = 'objectbuilds/objectbuild_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.case = get_object_or_404(Cases, pk=kwargs.get('case_pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        return context

    def form_valid(self, form):
        form.instance.cases = self.case
        messages.success(self.request, "比價建物已新增！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.case.pk])

class ObjectBuildUpdateView(LoginRequiredMixin, UpdateView):
    model = ObjectBuild
    form_class = ObjectBuildForm
    template_name = 'objectbuilds/objectbuild_form.html'

    def form_valid(self, form):
        messages.success(self.request, "比價建物已更新！")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('case_detail', args=[self.object.cases_id])

class ObjectBuildDeleteView(LoginRequiredMixin, DeleteView):
    model = ObjectBuild
    template_name = 'objectbuilds/objectbuild_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        case_id = self.object.cases_id
        messages.success(self.request, "比價建物已刪除！")
        response = super().delete(request, *args, **kwargs)
        self.success_url = reverse_lazy('case_detail', args=[case_id])
        return response

