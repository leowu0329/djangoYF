from django import forms
from .models import Cases, Land, Build, Person, Survey, FinalDecision, Result, ObjectBuild, Bouns, Auction, City, Township, OfficialDocuments
from users.models import CustomUser

COMPANY_CHOICES = [
	("揚富開發有限公司", "揚富開發有限公司"),
	("鉅鈦開發有限公司", "鉅鈦開發有限公司"),
]

STATUS_CHOICES = [
	("在途", "在途"),
	("結案", "結案"),
]

TYPE_USE_CHOICES = [
	("", ""),
	("公設", "公設"),
	("公寓-5樓含以下無電梯", "公寓-5樓含以下無電梯"),
	("透天厝", "透天厝"),
	("店面-店舖", "店面-店舖"),
	("辦公商業大樓", "辦公商業大樓"),
	("住宅大樓-11層含以上有電梯", "住宅大樓-11層含以上有電梯"),
	("華廈-10層含以下有電梯", "華廈-10層含以下有電梯"),
	("套房", "套房"),
	("農舍", "農舍"),
	("增建-持分後坪數打對折", "增建-持分後坪數打對折"),
]

USE_PARTITION_CHOICES = [
	("", ""),
	("第一種住宅區", "第一種住宅區"),
	("第二種住宅區", "第二種住宅區"),
	("第三種住宅區", "第三種住宅區"),
	("第四種住宅區", "第四種住宅區"),
	("第五種住宅區", "第五種住宅區"),
	("第一種商業區", "第一種商業區"),
	("第二種商業區", "第二種商業區"),
	("第三種商業區", "第三種商業區"),
	("第四種商業區", "第四種商業區"),
	("第二種工業區", "第二種工業區"),
	("第三種工業區", "第三種工業區"),
	("行政區", "行政區"),
	("文教區", "文教區"),
	("倉庫區", "倉庫區"),
	("風景區", "風景區"),
	("農業區", "農業區"),
	("保護區", "保護區"),
	("行水區", "行水區"),
	("保存區", "保存區"),
	("特定專用區", "特定專用區"),
]

PERSON_TYPE_CHOICES = [
	("債務人", "債務人"),
	("債權人", "債權人"),
]

FINAL_TYPE_CHOICES = [
	("區域負責人", "區域負責人"),
	("副署人員", "副署人員"),
]

WORK_AREA_CHOICES = [
	("雙北桃竹苗", "雙北桃竹苗"),
	("中彰投", "中彰投"),
	("雲嘉南", "雲嘉南"),
	("高高屏", "高高屏"),
]

FINAL_DECISION_CHOICES = [
	("未判定", "未判定"),
	("1拍", "1拍"),
	("2拍", "2拍"),
	("3拍", "3拍"),
	("4拍", "4拍"),
	("放棄", "放棄"),
]

class CasesForm(forms.ModelForm):
	company = forms.ChoiceField(
		choices=COMPANY_CHOICES,
		required=False,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='所屬公司',
	)

	status = forms.ChoiceField(
		choices=STATUS_CHOICES,
		required=False,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='案件狀態',
	)

	city = forms.ModelChoiceField(
		queryset=City.objects.all(),
		required=False,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='縣市',
	)

	township = forms.ModelChoiceField(
		queryset=Township.objects.all(), # Initial queryset, will be filtered by JS
		required=False,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='鄉鎮區里',
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		city_id = None
		if self.instance and self.instance.city: # For existing instances, get initial city from instance
			city_id = self.instance.city.id

		if self.is_bound: # If form is submitted, use data from POST
			city_id = self.data.get('city')

		if city_id:
			self.fields['township'].queryset = Township.objects.filter(city_id=city_id)
		else:
			self.fields['township'].queryset = Township.objects.all() # Or Township.objects.none() if no city is selected initially

	class Meta:
		model = Cases
		fields = [
			"caseNumber",
			"company",
			"city",
			"township",
			"bigSection",
			"smallSection",
			"village",
			"neighbor",
			"street",
			"section",
			"lane",
			"alley",
			"number",
			"Floor",
			"status",
		]

class LandForm(forms.ModelForm):
	class Meta:
		model = Land
		fields = [
			"landNumber",
			"url",
			"area",
			"holdingPointPersonal",
			"holdingPointAll",
			"remark",
		]
		widgets = {
			"landNumber": forms.TextInput(attrs={"class": "form-control"}),
			"url": forms.URLInput(attrs={"class": "form-control"}),
			"area": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
			"holdingPointPersonal": forms.NumberInput(attrs={"class": "form-control"}),
			"holdingPointAll": forms.NumberInput(attrs={"class": "form-control"}),
			"remark": forms.TextInput(attrs={"class": "form-control"}),
		}

class BuildForm(forms.ModelForm):
	typeUse = forms.ChoiceField(
		choices=TYPE_USE_CHOICES,
		required=False,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='建物型',
	)
	usePartition = forms.ChoiceField(
		choices=USE_PARTITION_CHOICES,
		required=False,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='使用分區',
	)

	class Meta:
		model = Build
		fields = [
			"buildNumber",
			"url",
			"area",
			"holdingPointPersonal",
			"holdingPointAll",
			"typeUse",
			"usePartition",
			"remark",
		]
		widgets = {
			"buildNumber": forms.TextInput(attrs={"class": "form-control"}),
			"url": forms.URLInput(attrs={"class": "form-control"}),
			"area": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
			"holdingPointPersonal": forms.NumberInput(attrs={"class": "form-control"}),
			"holdingPointAll": forms.NumberInput(attrs={"class": "form-control"}),
			"remark": forms.TextInput(attrs={"class": "form-control"}),
		}

class PersonForm(forms.ModelForm):
	type = forms.ChoiceField(
		choices=PERSON_TYPE_CHOICES,
		widget=forms.Select(attrs={"class": "form-select"}),
		label='分類',
	)
	class Meta:
		model = Person
		fields = ["name", "type", "phone"]
		widgets = {
			"name": forms.TextInput(attrs={"class": "form-control"}),
			"phone": forms.TextInput(attrs={"class": "form-control"}),
		}

class SurveyForm(forms.ModelForm):
	class Meta:
		model = Survey
		fields = [
			"firstDay",
			"secondDay",
			"foreclosureAnnouncementLink",
			"house988Link",
			"objectPhotoLink",
			"netMarketPriceLink",
			"foreclosureRecordLink",
			"objectViewLink",
			"pagesViewLink",
			"moneytViewLink",
		]
		widgets = {
			"firstDay": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
			"secondDay": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
			"foreclosureAnnouncementLink": forms.URLInput(attrs={"class": "form-control"}),
			"house988Link": forms.URLInput(attrs={"class": "form-control"}),
			"objectPhotoLink": forms.URLInput(attrs={"class": "form-control"}),
			"netMarketPriceLink": forms.URLInput(attrs={"class": "form-control"}),
			"foreclosureRecordLink": forms.URLInput(attrs={"class": "form-control"}),
			"objectViewLink": forms.URLInput(attrs={"class": "form-control"}),
			"pagesViewLink": forms.URLInput(attrs={"class": "form-control"}),
			"moneytViewLink": forms.URLInput(attrs={"class": "form-control"}),
		}

class FinalDecisionForm(forms.ModelForm):
	finalDecision = forms.ChoiceField(choices=FINAL_DECISION_CHOICES, widget=forms.Select(attrs={"class": "form-select"}), label='最終判定', required=False)
	type = forms.ChoiceField(choices=FINAL_TYPE_CHOICES, widget=forms.Select(attrs={"class": "form-select"}), label='分類', required=False)
	workArea = forms.ChoiceField(choices=WORK_AREA_CHOICES, widget=forms.Select(attrs={"class": "form-select"}), label='工作轄區', required=False)
	date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}), label='日期', required=False)
	class Meta:
		model = FinalDecision
		fields = ["finalDecision", "remark", "type", "name", "date", "workArea"]
		widgets = {
			"remark": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
			"name": forms.TextInput(attrs={"class": "form-control"}),
		}


class ResultForm(forms.ModelForm):
    actionResult = forms.ChoiceField(
        choices=[
            ("", ""),
            ("撤回", "撤回"),
            ("第三人搶標", "第三人搶標"),
            ("等待優購", "等待優購"),
            ("遭優購", "遭優購"),
            ("無人優購", "無人優購")
        ],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label='執行結果',
    )

    # Add a ChoiceField for bidAuctionTime
    bidAuctionTime = forms.ChoiceField(
        choices=[("", ""), ("1拍", "1拍"), ("2拍", "2拍"), ("3拍", "3拍"), ("4拍", "4拍")],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label='搶標拍別',
    )

    class Meta:
        model = Result
        fields = ["stopBuyDate", "actionResult", "bidAuctionTime", "bidMoney", "objectNumber"]
        widgets = {
            "stopBuyDate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "bidMoney": forms.NumberInput(attrs={"class": "form-control"}),
            "objectNumber": forms.TextInput(attrs={"class": "form-control"}),
        }


class ObjectBuildForm(forms.ModelForm):
	type = forms.ChoiceField(
		choices=[("自訂", "自訂"), ("實價登錄", "實價登錄"), ("好時價", "好時價")],
		widget=forms.Select(attrs={"class": "form-select"}),
		label='類型',
		required=False,
		initial='自訂',
	)
	transactionDate = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}), label='成交日期', required=False)

	class Meta:
		model = ObjectBuild
		fields = ["type", "address", "url", "houseAge", "transactionDate", "floorHeight", "totalPrice", "buildArea", "subBuildArea", "calculate", "cases"]
		widgets = {
			"cases": forms.HiddenInput(),
			"type": forms.Select(attrs={"class": "form-control"}),
		}

class BounsForm(forms.ModelForm):
    bounsPerson = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        label='勘查員',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'disabled': True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bounsPerson'].label_from_instance = lambda obj: obj.profile.nickname if hasattr(obj, 'profile') and obj.profile.nickname else obj.username
        
        # Set initial value for bounsPerson in the form
        if 'initial' in kwargs and 'bounsPerson' in kwargs['initial']:
            self.fields['bounsPerson'].initial = kwargs['initial']['bounsPerson']
        elif self.instance and self.instance.bounsPerson:
            self.fields['bounsPerson'].initial = self.instance.bounsPerson


    class Meta:
        model = Bouns
        fields = ('objectbuild', 'bounsPerson', 'bounsRate', 'bounsReason')
        widgets = {
            'objectbuild': forms.HiddenInput(),
        }

class AuctionForm(forms.ModelForm):
	type = forms.ChoiceField(
		choices=[("1拍", "1拍"), ("2拍", "2拍"), ("3拍", "3拍"), ("4拍", "4拍")],
		widget=forms.Select(attrs={"class": "form-select"}),
		label='拍別',
		required=False,
	)
	class Meta:
		model = Auction
		fields = ('cases', 'type', 'auctionDate', 'floorPrice', 'pingPrice', 'CP', 'click', 'monitor', 'caseCount', 'margin')
		widgets = {
			'cases': forms.HiddenInput(),
			'auctionDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
			'floorPrice': forms.NumberInput(attrs={'class': 'form-control'}),
			'pingPrice': forms.NumberInput(attrs={'class': 'form-control', 'disabled': True}),
			'CP': forms.NumberInput(attrs={'class': 'form-control', 'disabled': True}),
			'click': forms.NumberInput(attrs={'class': 'form-control'}),
			'monitor': forms.NumberInput(attrs={'class': 'form-control'}),
			'caseCount': forms.NumberInput(attrs={'class': 'form-control'}),
			'margin': forms.NumberInput(attrs={'class': 'form-control'}),
		}


class OfficialDocumentForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=OfficialDocuments.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label='案別',
    )
    stock = forms.ChoiceField(
        choices=OfficialDocuments.STOCK_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label='股別',
    )
    class Meta:
        model = OfficialDocuments
        fields = ['cases', 'type', 'stock', 'docNumber', 'tel', 'ext']
        widgets = {
            'cases': forms.HiddenInput(),
            'tel': forms.TextInput(attrs={'class': 'form-control'}),
            'ext': forms.TextInput(attrs={'class': 'form-control'}),
            'docNumber': forms.TextInput(attrs={'class': 'form-control'}),
        }
