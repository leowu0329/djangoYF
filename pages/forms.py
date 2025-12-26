from django import forms
from django.db.models import Q
from .models import Cases, Land, Build, Person, Survey, FinalDecision, Result, ObjectBuild, Bouns, Auction, City, Township, OfficialDocuments, Peterpen
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
	("共有人", "共有人"),
	("小飛俠", "小飛俠"),
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
		
		# 修改欄位標籤名稱
		self.fields['bigSection'].label = '段名'
		self.fields['smallSection'].label = '小段名'
		self.fields['section'].label = '幾段'
		
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
	user_select = forms.ChoiceField(
		choices=[],
		widget=forms.Select(attrs={"class": "form-select"}),
		label='選擇人員',
		required=False,
		help_text='可選擇現有用戶或自行輸入姓名'
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		# 檢查當前類型
		instance = getattr(self, 'instance', None) or kwargs.get('instance')
		current_type = None
		if instance and hasattr(instance, 'pk') and instance.pk:
			# 編輯模式，使用實例的類型
			current_type = instance.type
		elif hasattr(self, 'data') and self.data and 'type' in self.data:
			# 表單已提交，使用提交的數據
			current_type = self.data['type']
		elif hasattr(self, 'initial') and self.initial and 'type' in self.initial:
			# 使用初始值
			current_type = self.initial['type']
		else:
			# 新增模式，預設為「小飛俠」
			current_type = '小飛俠'
			self.fields['type'].initial = '小飛俠'
		
		# 根據類型設置選項
		choices = []
		
		if current_type == '債務人':
			# 債務人：只有自行輸入選項
			choices = [("", "--- 請自行輸入 ---")]
		elif current_type == '小飛俠':
			# 小飛俠：所有 Peterpen 的 name
			choices = [("", "--- 請選擇或自行輸入 ---")]
			peterpens = Peterpen.objects.all().order_by('name')
			for peterpen in peterpens:
				choices.append((peterpen.name, peterpen.name))
		elif current_type in ['債權人', '共有人']:
			# 債權人/共有人：CustomUser(is_staff=True) 對應的 Profile.nickname，也可自行輸入
			choices = [("", "--- 請選擇或自行輸入 ---")]
			staff_users = CustomUser.objects.filter(is_staff=True).select_related('profile')
			for user in staff_users:
				display_name = user.profile.nickname if hasattr(user, 'profile') and user.profile.nickname else user.username
				choices.append((display_name, display_name))
		else:
			# 創建模式且未選擇類型時，顯示 is_staff=True 的 CustomUser 的 profile.nickname
			choices = [("", "--- 請選擇或自行輸入 ---")]
			staff_users = CustomUser.objects.filter(is_staff=True).select_related('profile')
			for user in staff_users:
				display_name = user.profile.nickname if hasattr(user, 'profile') and user.profile.nickname else user.username
				choices.append((display_name, display_name))
		
		# 編輯模式：如果現有的 name 值不在選項列表中，將它添加到選項中
		if instance and hasattr(instance, 'pk') and instance.pk and instance.name:
			existing_name = instance.name.strip()
			if existing_name:
				# 檢查現有的 name 是否已經在選項中
				choice_values = [choice[0] for choice in choices]
				if existing_name not in choice_values:
					# 如果不在選項中，添加到選項列表
					choices.append((existing_name, existing_name))
		
		self.fields['user_select'].choices = choices
		
		# 如果表單已提交，檢查提交的 user_select 值是否在選項中，如果不在則添加
		if self.is_bound and 'user_select' in self.data:
			submitted_value = self.data.get('user_select', '').strip()
			if submitted_value:
				choice_values = [choice[0] for choice in self.fields['user_select'].choices]
				if submitted_value not in choice_values:
					# 如果不在選項中，添加到選項列表
					self.fields['user_select'].choices = list(self.fields['user_select'].choices) + [(submitted_value, submitted_value)]

	class Meta:
		model = Person
		fields = ["name", "type", "phone", "holdingShareNumerator", "holdingShareDenominator", "investmentNumerator", "investmentDenominator", "remark"]
		widgets = {
			"name": forms.TextInput(attrs={"class": "form-control", "id": "id_name"}),
			"phone": forms.TextInput(attrs={"class": "form-control"}),
			"holdingShareNumerator": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
			"holdingShareDenominator": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
			"investmentNumerator": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
			"investmentDenominator": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "1"}),
			"remark": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
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
	date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}), label='日期', required=False)
	name = forms.ChoiceField(choices=[], widget=forms.Select(attrs={"class": "form-select"}), label='人員', required=False)

	def __init__(self, *args, **kwargs):
		self.is_create = kwargs.pop('is_create', False)
		super().__init__(*args, **kwargs)
		
		# 如果是创建模式，移除分类、人员、日期字段
		if self.is_create:
			if 'type' in self.fields:
				del self.fields['type']
			if 'name' in self.fields:
				del self.fields['name']
			if 'date' in self.fields:
				del self.fields['date']
		else:
			# 編輯模式：保留所有字段
			# 獲取所有 is_active=True 且 is_staff=True 的用戶
			# 使用 nickname（如果有的話）或 username 作為值和顯示名稱
			active_staff_users = CustomUser.objects.filter(is_active=True, is_staff=True).select_related('profile')
			choices = [("", "")]
			for user in active_staff_users:
				display_name = user.profile.nickname if hasattr(user, 'profile') and user.profile.nickname else user.username
				# 使用 nickname 或 username 作為值
				choices.append((display_name, display_name))
			self.fields['name'].choices = choices
			
			# 處理編輯模式：如果實例有 name 值，直接使用（因為現在存儲的就是 nickname 或 username）
			if self.instance and self.instance.pk and self.instance.name:
				self.fields['name'].initial = self.instance.name

	class Meta:
		model = FinalDecision
		fields = ["finalDecision", "remark", "type", "name", "date"]
		widgets = {
			"remark": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
		}


class ResultForm(forms.ModelForm):
    actionResult = forms.ChoiceField(
        choices=[
            ("", ""),
            ("撤回", "撤回"),
            ("第三人搶標", "第三人搶標"),
            ("等待優購", "等待優購"),
            ("遭優購", "遭優購"),
            ("無人優購", "無人優購"),
            ("四拍流標", "四拍流標"),
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
    
    bounsRate = forms.ChoiceField(
        choices=[
            ("0.00", "0%"),
            ("0.05", "+5%"),
            ("0.10", "+10%"),
            ("-0.05", "-5%"),
            ("-0.10", "-10%"),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='加成',
        initial="0.00",
    )
    
    bounsReason = forms.ChoiceField(
        choices=[
            ("", ""),
            ("屋況", "屋況"),
            ("臨路寬度", "臨路寬度"),
            ("連外方便性", "連外方便性"),
            ("房價走勢", "房價走勢"),
            ("其他", "其他"),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_bounsReason'}),
        label='加成原因',
    )
    
    bounsReasonOther = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_bounsReasonOther'}),
        label='其他原因',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bounsPerson'].label_from_instance = lambda obj: obj.profile.nickname if hasattr(obj, 'profile') and obj.profile.nickname else obj.username
        
        # Set initial value for bounsPerson in the form
        # Priority: instance value > initial kwargs value
        if self.instance and self.instance.pk and self.instance.bounsPerson:
            # For update view, use the instance's bounsPerson
            self.fields['bounsPerson'].initial = self.instance.bounsPerson
        elif 'initial' in kwargs and 'bounsPerson' in kwargs['initial']:
            # For create view, use initial value
            self.fields['bounsPerson'].initial = kwargs['initial']['bounsPerson']
        
        # Set initial value for bounsRate in the form
        if self.instance and self.instance.bounsRate is not None:
            # Convert Decimal to string for ChoiceField
            rate_value = f"{self.instance.bounsRate:.2f}"
            # Check if the value exists in choices, otherwise default to "0.00"
            valid_choices = [choice[0] for choice in self.fields['bounsRate'].choices]
            if rate_value in valid_choices:
                self.fields['bounsRate'].initial = rate_value
            else:
                self.fields['bounsRate'].initial = "0.00"
        
        # Set initial value for bounsReason in the form
        # Check if the current value is one of the predefined choices
        if self.instance and self.instance.pk and self.instance.bounsReason:
            predefined_choices = ["", "屋況", "臨路寬度", "連外方便性", "房價走勢", "其他"]
            if self.instance.bounsReason in predefined_choices:
                self.fields['bounsReason'].initial = self.instance.bounsReason
                # If it's "其他" but we don't have a custom value, it might have been saved as "其他"
                # In this case, we should check if there's a custom value in the database
                # For now, we'll let the user enter a new value if needed
            else:
                # If the value is not in predefined choices, it's a custom "其他" value
                self.fields['bounsReason'].initial = "其他"
                self.fields['bounsReasonOther'].initial = self.instance.bounsReason
    
    def clean_bounsRate(self):
        """Convert string choice value to Decimal for model field"""
        from decimal import Decimal
        value = self.cleaned_data.get('bounsRate')
        if value and value != "":
            return Decimal(value)
        return Decimal('0.00')
    
    def clean(self):
        """Handle '其他' option for bounsReason"""
        cleaned_data = super().clean()
        bounsReason = cleaned_data.get('bounsReason')
        bounsReasonOther = cleaned_data.get('bounsReasonOther')
        
        if bounsReason == "其他":
            if not bounsReasonOther or bounsReasonOther.strip() == "":
                raise forms.ValidationError({'bounsReasonOther': '請輸入其他原因'})
            # Save the custom text to bounsReason
            cleaned_data['bounsReason'] = bounsReasonOther.strip()
        elif bounsReasonOther:
            # Clear bounsReasonOther if not "其他" is selected
            cleaned_data['bounsReasonOther'] = ""
        
        return cleaned_data


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
