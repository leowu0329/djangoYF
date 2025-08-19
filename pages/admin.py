from django.contrib import admin
from django import forms
from .models import Cases, Land, Build, Result
from .forms import TYPE_USE_CHOICES, USE_PARTITION_CHOICES

class LandInline(admin.TabularInline):
    model = Land
    extra = 1

class BuildAdminForm(forms.ModelForm):
    typeUse = forms.ChoiceField(choices=TYPE_USE_CHOICES, required=False)
    usePartition = forms.ChoiceField(choices=USE_PARTITION_CHOICES, required=False)

    class Meta:
        model = Build
        fields = "__all__"

class BuildInline(admin.TabularInline):
    model = Build
    extra = 1
    form = BuildAdminForm

@admin.register(Cases)
class CasesAdmin(admin.ModelAdmin):
    list_display = ("caseNumber", "company", "status", "updated")
    search_fields = ("caseNumber", "company", "city", "township")
    list_filter = ("company", "status", "city")
    inlines = [LandInline, BuildInline]

@admin.register(Land)
class LandAdmin(admin.ModelAdmin):
    list_display = ("cases", "landNumber", "area", "holdingPointPersonal", "holdingPointAll", "calculatedArea", "updated")
    search_fields = ("landNumber", "cases__caseNumber")
    list_filter = ("cases",)

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    form = BuildAdminForm
    list_display = ("cases", "buildNumber", "area", "holdingPointPersonal", "holdingPointAll", "calculatedArea", "typeUse", "usePartition", "updated")
    search_fields = ("buildNumber", "cases__caseNumber")
    list_filter = ("cases", "typeUse", "usePartition")


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("cases", "stopBuyDate", "actionResult", "bidAuctionTime", "bidMoney", "objectNumber", "updated")
    search_fields = ("objectNumber", "cases__caseNumber")
    list_filter = ("cases", "actionResult", "stopBuyDate")
