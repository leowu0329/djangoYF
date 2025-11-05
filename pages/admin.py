from django.contrib import admin
from django import forms
from import_export.admin import ImportExportModelAdmin
from django import forms
from import_export.formats import base_formats # Import base_formats
from import_export import resources, fields, widgets # Import resources, fields, and widgets
from .models import Cases, Land, Build, Result, City, Township, Person, Survey, FinalDecision, ObjectBuild, Bouns, Auction, OfficialDocuments
from .forms import TYPE_USE_CHOICES, USE_PARTITION_CHOICES

# 確保導入正確的格式類（備用方案）
try:
    from tablib.formats import JSONFormat, CSVFormat, XLSXFormat
except ImportError:
    # 如果直接導入失敗，使用格式註冊表
    try:
        from tablib.formats import registry
        JSONFormat = registry.get_format('json')
        CSVFormat = registry.get_format('csv')
        XLSXFormat = registry.get_format('xlsx')
    except ImportError:
        # 如果所有方法都失敗，使用 django-import-export 的格式
        JSONFormat = base_formats.JSON
        CSVFormat = base_formats.CSV
        XLSXFormat = base_formats.XLSX

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

class CasesAdminForm(forms.ModelForm):
    class Meta:
        model = Cases
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始時，若已有 city，限制 township 查詢集；否則清空
        city_id = None
        if self.instance and self.instance.pk and self.instance.city_id:
            city_id = self.instance.city_id
        if self.is_bound:
            city_id = self.data.get("city") or city_id
        if city_id:
            self.fields["township"].queryset = Township.objects.filter(city_id=city_id).order_by("name")
        else:
            self.fields["township"].queryset = Township.objects.none()

    class Media:
        js = ("pages/admin_cases.js?v=20251105",)


@admin.register(Cases)
class CasesAdmin(ImportExportModelAdmin):
    form = CasesAdminForm
    list_display = ("caseNumber", "company", "status", "updated")
    search_fields = ("caseNumber", "company", "city", "township")
    list_filter = ("company", "status", "city")
    inlines = [LandInline, BuildInline]

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]  # 使用 django-import-export 的格式類

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]  # 使用 django-import-export 的格式類

@admin.register(Land)
class LandAdmin(ImportExportModelAdmin):
    list_display = ("cases", "landNumber", "area", "holdingPointPersonal", "holdingPointAll", "calculatedArea", "updated")
    search_fields = ("landNumber", "cases__caseNumber")
    list_filter = ("cases",)

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Build)
class BuildAdmin(ImportExportModelAdmin):
    form = BuildAdminForm
    list_display = ("cases", "buildNumber", "area", "holdingPointPersonal", "holdingPointAll", "calculatedArea", "typeUse", "usePartition", "updated")
    search_fields = ("buildNumber", "cases__caseNumber")
    list_filter = ("cases", "typeUse", "usePartition")

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Result)
class ResultAdmin(ImportExportModelAdmin):
    list_display = ("cases", "stopBuyDate", "actionResult", "bidAuctionTime", "bidMoney", "objectNumber", "updated")
    search_fields = ("objectNumber", "cases__caseNumber")
    list_filter = ("cases", "actionResult", "stopBuyDate")

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Township)
class TownshipAdmin(ImportExportModelAdmin):
    list_display = ("name", "city", "zip_code", "district_court")
    search_fields = ("name", "city__name", "zip_code")
    list_filter = ("city",)

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    list_display = ('cases', 'name', 'type', 'phone', 'created', 'updated')
    search_fields = ('name', 'cases__caseNumber', 'phone')
    list_filter = ('type', 'cases')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin):
    list_display = ('cases', 'firstDay', 'secondDay', 'foreclosureAnnouncementLink', 'house988Link', 'objectPhotoLink', 'created', 'updated')
    search_fields = ('cases__caseNumber', 'firstDay', 'secondDay')
    list_filter = ('cases', 'firstDay', 'secondDay')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

class FinalDecisionResource(resources.ModelResource):
    date = fields.Field(attribute='date', column_name='日期', widget=widgets.DateWidget(format='%Y-%m-%d'))

    class Meta:
        model = FinalDecision
        fields = ('id', 'cases', 'finalDecision', 'type', 'name', 'date', 'workArea', 'remark', 'created', 'updated')
        export_order = ('id', 'cases', 'finalDecision', 'type', 'name', 'date', 'workArea', 'remark', 'created', 'updated')

@admin.register(FinalDecision)
class FinalDecisionAdmin(ImportExportModelAdmin):
    resource_class = FinalDecisionResource
    list_display = ('cases', 'finalDecision', 'type', 'name', 'date', 'workArea', 'created', 'updated')
    search_fields = ('cases__caseNumber', 'finalDecision', 'name', 'workArea')
    list_filter = ('finalDecision', 'type', 'workArea', 'cases')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(ObjectBuild)
class ObjectBuildAdmin(ImportExportModelAdmin):
    list_display = ('cases', 'type', 'address', 'houseAge', 'totalPrice', 'buildArea', 'unitPrice', 'calculate', 'created', 'updated')
    search_fields = ('cases__caseNumber', 'address', 'type')
    list_filter = ('type', 'cases')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Bouns)
class BounsAdmin(ImportExportModelAdmin):
    list_display = ('objectbuild', 'bounsPerson', 'bounsRate', 'bounsReason', 'updated', 'timestamp')
    search_fields = ('objectbuild__cases__caseNumber', 'bounsPerson', 'bounsReason')
    list_filter = ('bounsPerson', 'objectbuild__cases')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

@admin.register(Auction)
class AuctionAdmin(ImportExportModelAdmin):
    list_display = ('cases', 'type', 'auctionDate', 'floorPrice', 'pingPrice', 'CP', 'created', 'updated')
    search_fields = ('cases__caseNumber', 'type')
    list_filter = ('type', 'auctionDate', 'cases')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

class OfficialDocumentsResource(resources.ModelResource):
    cases = fields.Field(attribute='cases', column_name='案件編號', widget=widgets.ForeignKeyWidget(Cases, 'caseNumber'))

    class Meta:
        model = OfficialDocuments
        fields = ('id', 'cases', 'docNumber', 'type', 'stock', 'tel', 'ext', 'created', 'updated')
        export_order = ('id', 'cases', 'docNumber', 'type', 'stock', 'tel', 'ext', 'created', 'updated')

@admin.register(OfficialDocuments)
class OfficialDocumentsAdmin(ImportExportModelAdmin):
    resource_class = OfficialDocumentsResource
    list_display = ('cases', 'docNumber', 'type', 'stock', 'tel', 'ext', 'created', 'updated')
    search_fields = ('cases__caseNumber', 'docNumber', 'type', 'stock')
    list_filter = ('type', 'stock', 'cases')

    def get_import_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]

    def get_export_formats(self):
        return [base_formats.XLSX, base_formats.CSV, base_formats.JSON]