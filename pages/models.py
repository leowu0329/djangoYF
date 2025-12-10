from django.db import models
from django.urls import reverse
from decimal import Decimal, InvalidOperation, DivisionByZero

# Create your models here.


class Cases(models.Model):
  caseNumber=models.CharField(u'案號(*)',max_length=100)
  company=models.CharField(u'所屬公司',max_length=50,null=True,blank=True)
  city=models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=u'縣市')
  township=models.ForeignKey('Township', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=u'鄉鎮區里')
  bigSection=models.CharField(u'段號',max_length=10,null=True,blank=True)
  smallSection=models.CharField(u'小段',max_length=10,null=True,blank=True)
  village=models.CharField(u'村里',max_length=100,null=True,blank=True)
  neighbor=models.CharField(u'鄰',max_length=100,null=True,blank=True)
  street=models.CharField(u'街路',max_length=100,null=True,blank=True)
  section=models.CharField(u'段',max_length=100,null=True,blank=True)
  lane=models.CharField(u'巷',max_length=100,null=True,blank=True)
  alley=models.CharField(u'弄',max_length=100,null=True,blank=True)
  number=models.CharField(u'號',max_length=100,null=True)
  Floor=models.CharField(u'樓(含之幾)',max_length=100,null=True,blank=True)
  status = models.CharField(u'案件狀態',max_length=10,null=True,blank=True)
  updated = models.DateTimeField(u'案件最後更新時間',auto_now=True,auto_now_add=False)
  timestamp = models.DateTimeField(u'案件建立時間',auto_now=False,auto_now_add=True)
  user = models.ForeignKey('users.CustomUser',verbose_name = u'區域負責人', on_delete=models.CASCADE)

  def __str__(self):
    return self.caseNumber

  def get_absolute_url(self):
    return reverse('case_detail', args=[str(self.id)])

  @property
  def survey_links_count_display(self):
    total_links_count = 0
    for survey in self.surveys.all():
        link_fields = [
            survey.foreclosureAnnouncementLink,
            survey.house988Link,
            survey.objectPhotoLink,
            survey.netMarketPriceLink,
            survey.foreclosureRecordLink,
            survey.objectViewLink,
            survey.pagesViewLink,
            survey.moneytViewLink,
        ]
        # Count non-empty links for the current survey
        total_links_count += sum(1 for field in link_fields if field)

    if total_links_count > 0:
        return f"(連結：{total_links_count})"
    return "(0)"

  def save(self, *args, **kwargs):
    # 處理 bigSection
    if self.bigSection:
      bigSection = str(self.bigSection)
      if "段" not in bigSection:
        self.bigSection = bigSection + "段"
    # 處理 smallSection
    if self.smallSection:
      smallSection = str(self.smallSection)
      if "小段" not in smallSection:
        self.smallSection = smallSection + "小段"
    # 處理 village
    if self.village:
      village = str(self.village)
      if "村" not in village and "里" not in village:
        self.village = village + "里"
    # 處理 neighbor
    if self.neighbor:
      neighbor = str(self.neighbor)
      if "鄰" not in neighbor:
        self.neighbor = neighbor + "鄰"
    # 處理 street
    if self.street:
      street = str(self.street)
      if "街" not in street and "路" not in street:
        self.street = street + "路"
    # 處理 section
    if self.section:
      section = str(self.section)
      if "段" not in section:
        self.section = section + "段"
    # 處理 lane
    if self.lane:
      lane = str(self.lane)
      if "巷" not in lane:
        self.lane = lane + "巷"
    # 處理 alley
    if self.alley:
      alley = str(self.alley)
      if "弄" not in alley:
        self.alley = alley + "弄"
    # 處理 number
    if self.number:
      number = str(self.number)
      if "號" not in number:
        self.number = number + "號"
    super().save(*args, **kwargs)

  def fullAddress(self):
    def _is_valid(value):
      return value and value.strip().upper() != 'NULL'

    if self.township:
      township_part = self.township.name
    else:
      township_part = ''

    address_parts = [
        self.city.name if self.city else '',
        township_part,
        self.village,
        self.neighbor,
        self.street,
        self.section,
        self.lane,
        self.alley,
        self.number,
        self.Floor
    ]
    # Filter out empty strings and the string 'NULL'
    return ''.join(filter(_is_valid, address_parts))

  @property
  def case_number_and_address(self):
    return f"{self.caseNumber}\n{self.fullAddress()}"

  @property
  def total_calculated_land_area_display(self):
    from django.db.models import Sum # Import Sum here
    total_calculated_area = self.lands.aggregate(Sum('calculatedArea'))['calculatedArea__sum']
    if total_calculated_area is None or total_calculated_area == Decimal('0'):
      return "無記錄"
    return f"{total_calculated_area.quantize(Decimal('0.01'))} 坪"

  @property
  def total_calculated_build_area_display(self):
    from django.db.models import Sum # Import Sum here
    total_calculated_area = self.builds.aggregate(Sum('calculatedArea'))['calculatedArea__sum']
    if total_calculated_area is None or total_calculated_area == Decimal('0'):
      return "無記錄"
    return f"{total_calculated_area.quantize(Decimal('0.01'))} 坪"

  @property
  def people_summary_display(self):
    from django.db.models import Count # Import Count here
    debtors_count = self.people.filter(type='債務人').count()
    creditors_count = self.people.filter(type='債權人').count()
    co_owners_count = self.people.filter(type='共有人').count()
    return f"債務人({debtors_count})/債權人({creditors_count})/共有人({co_owners_count})"

  @property
  def avg_objectbuild_calculate_display(self):
    from django.db.models import Avg
    avg_value = self.objectbuilds.aggregate(Avg('calculate'))['calculate__avg']
    if avg_value is not None:
      return f"時價：{int(avg_value)}元"
    return "無記錄"

  @property
  def result_action_result_display(self):
    latest_result = self.results.order_by('-created').first()
    if latest_result and latest_result.actionResult:
      return f"{latest_result.actionResult}"
    return "無記錄"

  @property
  def has_objectbuild_records(self):
    return self.objectbuilds.exists()

  def __str__(self):
    return self.caseNumber

  def get_absolute_url(self):
    return reverse('case_detail', args=[str(self.id)])

class City(models.Model):
  name = models.CharField(u'城市',max_length=30)

  def __str__(self):
    return self.name

  class Meta:
    # managed = True
    db_table = 'yfcase_city'

class Township(models.Model):
  city = models.ForeignKey(City, on_delete=models.CASCADE)
  name = models.CharField(u'鄉鎮',max_length=30)
  zip_code = models.CharField(u'郵遞區號',max_length=30)
  district_court = models.CharField(u'地方法院',max_length=30)
  land_office  = models.CharField(u'地政事務所',max_length=30)
  finance_and_tax_bureau = models.CharField(u'財政稅務局',max_length=30)
  police_station = models.CharField(u'警察局',max_length=30)
  irs = models.CharField(u'國稅局',max_length=30)
  home_office = models.CharField(u'戶政事務所',max_length=30)

  def __str__(self):
    return self.name

  class Meta:
    # managed = True
    db_table = 'yfcase_township'


class Land(models.Model):
  cases = models.ForeignKey(Cases, related_name='lands', on_delete=models.CASCADE, verbose_name=u'案件')
  landNumber = models.CharField(u'地號', max_length=100, null=True)
  url = models.URLField(u'謄本', max_length=200, null=True, blank=True)
  area = models.DecimalField(u'地坪(平方公尺)', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  holdingPointPersonal = models.DecimalField(u'個人持分', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  holdingPointAll = models.DecimalField(u'所有持分', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  remark = models.CharField(u'備註', max_length=100, null=True, blank=True)
  calculatedArea = models.DecimalField(u'計算後地坪(坪)', default=0, max_digits=12, decimal_places=2, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  @property
  def formatted_landNumber(self):
    if self.cases and self.cases.bigSection:
      return f"{self.cases.bigSection}{self.landNumber}"
    return self.landNumber

  def save(self, *args, **kwargs):
    try:
      personal = Decimal(self.holdingPointPersonal or 0)
      total = Decimal(self.holdingPointAll or 0)
      area_m2 = Decimal(self.area or 0)
      if total and area_m2:
        # (holdingPointPersonal / holdingPointAll) * area * 0.3025
        self.calculatedArea = (personal / total) * area_m2 * Decimal('0.3025')
      else:
        self.calculatedArea = Decimal('0')
    except (InvalidOperation, DivisionByZero):
      self.calculatedArea = Decimal('0')
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.landNumber or ''}"


class Build(models.Model):
  cases = models.ForeignKey(Cases, related_name='builds', on_delete=models.CASCADE, verbose_name=u'案件')
  buildNumber = models.CharField(u'建號', max_length=100, null=True)
  url = models.URLField(u'謄本', max_length=200, null=True, blank=True)
  area = models.DecimalField(u'建坪(平方公尺)', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  holdingPointPersonal = models.DecimalField(u'個人持分', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  holdingPointAll = models.DecimalField(u'所有持分', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  calculatedArea = models.DecimalField(u'計算後建坪', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  typeUse = models.CharField(u'建物型', max_length=100, null=True, blank=True)
  usePartition = models.CharField(u'使用分區', max_length=100, null=True, blank=True)
  remark = models.CharField(u'備註', max_length=100, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  @property
  def formatted_buildNumber(self):
    if self.cases and self.cases.bigSection:
      return f"{self.cases.bigSection}{self.buildNumber}"
    return self.buildNumber

  def save(self, *args, **kwargs):
    try:
      personal = Decimal(self.holdingPointPersonal or 0)
      total = Decimal(self.holdingPointAll or 0)
      area_m2 = Decimal(self.area or 0)
      if total and area_m2:
        base = (personal / total) * area_m2 * Decimal('0.3025')
        if (self.typeUse or '') == '增建-持分後坪數打對折':
          base = base / Decimal('2')
        elif (self.typeUse or '') == '公設':
          base = base / Decimal('4')
        self.calculatedArea = base
      else:
        self.calculatedArea = Decimal('0')
    except (InvalidOperation, DivisionByZero):
      self.calculatedArea = Decimal('0')
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.buildNumber or ''}"


class Person(models.Model):
  cases = models.ForeignKey(Cases, related_name='people', on_delete=models.CASCADE, verbose_name=u'案件')
  name = models.CharField(u'姓名', max_length=30)
  type = models.CharField(u'分類', max_length=30)
  phone = models.CharField(u'電話', max_length=30, null=True, blank=True)
  holdingShareNumerator = models.PositiveIntegerField(u'持分比例(個人)', null=True, blank=True)
  holdingShareDenominator = models.PositiveIntegerField(u'持分比例(所有)', null=True, blank=True)
  investmentNumerator = models.PositiveIntegerField(u'投資比例(個人)', null=True, blank=True)
  investmentDenominator = models.PositiveIntegerField(u'投資比例(所有)', null=True, blank=True)
  remark = models.CharField(u'備註', max_length=500, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def __str__(self):
    return f"{self.name} ({self.type})"


class Survey(models.Model):
  cases = models.ForeignKey(Cases, related_name='surveys', on_delete=models.CASCADE, verbose_name=u'案件')
  firstDay = models.DateField(u'初勘日', null=True, blank=True)
  secondDay = models.DateField(u'會勘日', null=True, blank=True)
  foreclosureAnnouncementLink = models.URLField(u'法拍公告(證物三)', max_length=1000, null=True, blank=True)
  house988Link = models.URLField(u'998連結', max_length=1000, null=True, blank=True)
  objectPhotoLink = models.URLField(u'物件照片(證物四)', max_length=1000, null=True, blank=True)
  netMarketPriceLink = models.URLField(max_length=1000, null=True, blank=True)
  foreclosureRecordLink = models.URLField(u'法拍記錄(證物七)', max_length=1000, null=True, blank=True)
  objectViewLink = models.URLField(u'標的物(現場勘查)', max_length=1000, null=True, blank=True)
  pagesViewLink = models.URLField(u'收發文薄', max_length=1000, null=True, blank=True)
  moneytViewLink = models.URLField(u'流水帳', max_length=1000, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def __str__(self):
    return f"{self.cases.caseNumber} Survey"


class FinalDecision(models.Model):
  cases = models.ForeignKey(Cases, related_name='finaldecisions', on_delete=models.CASCADE, verbose_name=u'案件')
  finalDecision = models.CharField(u'最終判定', max_length=10, null=True, blank=True)
  remark = models.CharField(u'備註', max_length=3000, null=True, blank=True)
  type = models.CharField(u'分類', max_length=3000, null=True, blank=True)
  name = models.CharField(u'人員', max_length=150, null=True, blank=True)
  date = models.DateField(u'日期', null=True, blank=True)
  workArea = models.CharField(u'工作轄區', max_length=10, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.finalDecision or ''}"


class Result(models.Model):
  ACTION_RESULT_CHOICES = [
    ("", ""),
    ("撤回", "撤回"),
    ("第三人搶標", "第三人搶標"),
    ("等待優購", "等待優購"),
    ("遭優購", "遭優購"),
    ("無人優購", "無人優購"),
    ("四拍流標", "四拍流標")
  ]

  cases = models.ForeignKey(Cases, related_name='results', on_delete=models.CASCADE, verbose_name=u'案件')
  stopBuyDate = models.DateField(u'應買止日', null=True, blank=True)
  actionResult = models.CharField(u'執行結果', max_length=20, null=True, blank=True, choices=ACTION_RESULT_CHOICES)
  bidAuctionTime = models.CharField(u'搶標拍別', max_length=20, null=True, blank=True)
  bidMoney = models.DecimalField(u'搶標金額', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  objectNumber = models.CharField(u'標的編號', max_length=20, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.actionResult or ''}"


class ObjectBuild(models.Model):
  TYPE_CHOICES = [
    ("自訂", "自訂"),
    ("實價登錄", "實價登錄"),
    ("好時價", "好時價"),
  ]

  cases = models.ForeignKey(Cases, related_name='objectbuilds', on_delete=models.CASCADE, verbose_name=u'案件')
  type = models.CharField(u'類型', max_length=100, null=True, blank=True, choices=TYPE_CHOICES, default='自訂')
  address = models.CharField(u'地址', max_length=100, null=True, blank=True)
  url = models.URLField(u'附件', max_length=1000, null=True, blank=True)
  houseAge = models.DecimalField(u'屋齡(年)', default=0, max_digits=5, decimal_places=2, null=True, blank=True)
  transactionDate = models.DateField(u'成交日期', null=True, blank=True)
  floorHeight = models.CharField(u'樓高', max_length=100, null=True, blank=True)
  totalPrice = models.DecimalField(u'總價', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  buildArea = models.DecimalField(u'建坪(坪)', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  subBuildArea = models.DecimalField(u'增建坪數(坪)', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  unitPrice = models.DecimalField(u'單價', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  calculate = models.DecimalField(u'計算', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def _get_bounses_average_rate(self):
    from django.db.models import Avg # Moved import inside function as it's not a global constant
    # Using 'bounses' as related_name
    average_rate = self.bounses.aggregate(Avg('bounsRate'))['bounsRate__avg']
    return Decimal(average_rate or 0)

  def save(self, *args, **kwargs):
    is_new = self._state.adding # Check if this is a new instance

    # Step 1: Calculate unitPrice before initial save (if it's a new instance or relevant fields changed)
    try:
      total_price = Decimal(self.totalPrice or 0)
      build_area = Decimal(self.buildArea or 0)
      sub_build_area = Decimal(self.subBuildArea or 0)
      print(f"ObjectBuild Save (pre-save): total_price={total_price}, build_area={build_area}, sub_build_area={sub_build_area}")

      denominator = build_area + (sub_build_area / Decimal('2'))
      if denominator and denominator != 0:
        self.unitPrice = (total_price / denominator).quantize(Decimal('1'))
      else:
        self.unitPrice = Decimal('0')
      print(f"ObjectBuild Save (pre-save): unitPrice={self.unitPrice}")
    except (InvalidOperation, DivisionByZero) as e:
      print(f"Error in ObjectBuild pre-save calculation: {e}")
      self.unitPrice = Decimal('0')

    # Step 2: Save the instance to ensure it has a primary key
    super().save(*args, **kwargs)

    # Step 3: Calculate 'calculate' field AFTER the instance has a PK
    try:
      bouns_avg = self._get_bounses_average_rate()
      print(f"ObjectBuild Save (post-save): bouns_avg={bouns_avg}")
      new_calculate_value = (bouns_avg + Decimal('1')) * (self.unitPrice or 0)
      print(f"ObjectBuild Save (post-save): new_calculate_value={new_calculate_value}")

      # Only save if the calculate value has actually changed to avoid infinite loops
      if self.calculate != new_calculate_value:
        self.calculate = new_calculate_value
        # Avoid calling self.save() directly to prevent recursion.
        # Use update_fields to save only the 'calculate' field.
        ObjectBuild.objects.filter(pk=self.pk).update(calculate=self.calculate)
        print(f"ObjectBuild Save (post-save): calculate updated via .update()")

    except (InvalidOperation, DivisionByZero) as e:
      print(f"Error in ObjectBuild post-save calculation: {e}")
      # Ensure calculate is set to 0 on error
      if self.calculate != Decimal('0'):
        self.calculate = Decimal('0')
        ObjectBuild.objects.filter(pk=self.pk).update(calculate=self.calculate)
        print(f"ObjectBuild Save (post-save): calculate set to 0 due to error via .update()")

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.address or ''}"

class Bouns(models.Model):
  objectbuild=models.ForeignKey(ObjectBuild,related_name='bounses',on_delete=models.CASCADE)
  bounsPerson= models.ForeignKey('users.CustomUser', verbose_name='勘查員', on_delete=models.SET_NULL, null=True, blank=True, related_name='bouns_set')
  bounsRate=models.DecimalField(u'加成',default=0,max_digits=4,decimal_places=2,null=True,blank=True)
  bounsReason = models.CharField(u'加成原因',max_length=100,null=True,blank=True)
  updated = models.DateTimeField(u'更新時間',auto_now=True,auto_now_add=False)
  timestamp = models.DateTimeField(u'建立時間',auto_now=False,auto_now_add=True)

  @property
  def display_bouns_person(self):
    if self.bounsPerson and hasattr(self.bounsPerson, 'profile') and self.bounsPerson.profile.nickname:
      return self.bounsPerson.profile.nickname
    elif self.bounsPerson:
      return self.bounsPerson.username
    return ""

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs) # Call the original save method
    self.objectbuild.save() # Trigger recalculation on related ObjectBuild

  def delete(self, *args, **kwargs):
    objectbuild_instance = self.objectbuild
    super().delete(*args, **kwargs) # Call the original delete method
    objectbuild_instance.save() # Trigger recalculation on related ObjectBuild

class Auction(models.Model):
  TYPE_CHOICES = [
    ("1拍", "1拍"),
    ("2拍", "2拍"),
    ("3拍", "3拍"),
    ("4拍", "4拍"),
  ]
  cases=models.ForeignKey(Cases,related_name='auctions',on_delete=models.CASCADE)
  type = models.CharField(u'拍別',max_length=10,null=True,blank=True, choices=TYPE_CHOICES)
  auctionDate = models.DateField(u'拍賣日',null=True,blank=True)
  floorPrice = models.DecimalField(u'底價',default=0,max_digits=10,decimal_places=0,null=True,blank=True)
  pingPrice = models.DecimalField(u'坪價',default=0,max_digits=10,decimal_places=0,null=True,blank=True)
  CP = models.DecimalField(u'CP',default=0,max_digits=10,decimal_places=2,null=True,blank=True)
  click = models.DecimalField(u'點閱',default=0,max_digits=4,decimal_places=0,null=True,blank=True)
  monitor = models.DecimalField(u'監控',default=0,max_digits=4,decimal_places=0,null=True,blank=True)
  caseCount = models.DecimalField(u'成交件數',default=0,max_digits=4,decimal_places=0,null=True,blank=True)
  margin = models.DecimalField(u'保証金',default=0,max_digits=10,decimal_places=0,null=True,blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def save(self, *args, **kwargs):
    from django.db.models import Sum, Avg # Import Sum and Avg inside the method
    super().save(*args, **kwargs) # Save first to ensure self.cases is available

    try:
      total_calculated_area = self.cases.builds.aggregate(Sum('calculatedArea'))['calculatedArea__sum']
      if total_calculated_area and total_calculated_area > 0:
        self.pingPrice = (self.floorPrice / total_calculated_area).quantize(Decimal('1'))
      else:
        self.pingPrice = Decimal('0')

      # Replace the existing CP calculation with the new property
      self.CP = self.calculated_cp_value

      Auction.objects.filter(pk=self.pk).update(pingPrice=self.pingPrice, CP=self.CP)

    except (InvalidOperation, DivisionByZero) as e:
      Auction.objects.filter(pk=self.pk).update(pingPrice=Decimal('0'), CP=Decimal('0'))

  @property
  def calculated_cp_value(self):
    from django.db.models import Avg
    try:
      avg_objectbuild_calculate = self.cases.objectbuilds.all().aggregate(Avg('calculate'))['calculate__avg']
      ping_price = self.pingPrice

      if ping_price and ping_price > 0 and avg_objectbuild_calculate is not None:
        return (Decimal(avg_objectbuild_calculate) / ping_price).quantize(Decimal('0.01'))
      else:
        return Decimal('0')
    except (InvalidOperation, DivisionByZero):
      return Decimal('0')

  @property
  def avg_objectbuild_calculate_display(self):
    from django.db.models import Avg
    filtered_objectbuilds = self.cases.objectbuilds.all()
    avg_value = filtered_objectbuilds.aggregate(Avg('calculate'))['calculate__avg']
    print(f"DEBUG: Auction.avg_objectbuild_calculate_display: raw_avg={avg_value}") # Re-added debug print
    if avg_value is not None:
      display_value = avg_value.quantize(Decimal('0.01'))
      print(f"DEBUG: Auction.avg_objectbuild_calculate_display: formatted_avg={display_value}") # Re-added debug print
      return display_value
    else:
      print(f"DEBUG: Auction.avg_objectbuild_calculate_display: returning 0") # Re-added debug print
      return Decimal('0') # Changed from None to Decimal('0')

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.type or ''} ({self.auctionDate or ''})"

  class Meta:
    ordering = ['auctionDate', 'id']


class OfficialDocuments(models.Model):
  TYPE_CHOICES = [
      ("法拍", "法拍"),
      ("分割共有物", "分割共有物"),
      ("不當得利", "不當得利"),
      ("遷讓房屋", "遷讓房屋"),
      ("訴訟費用額(利)", "訴訟費用額(利)"),
      ("訴訟費用額(割)", "訴訟費用額(割)"),
      ("訴訟費用額(遷)", "訴訟費用額(遷)"),
      ("強制執行(變價)", "強制執行(變價)"),
      ("強制執行(清償)", "強制執行(清償)"),
  ]
  STOCK_CHOICES = [
      ("忠", "忠"),
      ("孝", "孝"),
  ]
  cases=models.ForeignKey(Cases,related_name='officialdocuments',on_delete=models.CASCADE)
  docNumber = models.CharField(u'案號',max_length=100,null=True,blank=True)
  type = models.CharField(u'案別',max_length=100,null=True,blank=True, choices=TYPE_CHOICES, default="法拍")
  stock = models.CharField(u'股別',max_length=100,null=True,blank=True, choices=STOCK_CHOICES, default="忠")
  tel = models.CharField(u'電話',max_length=100,null=True,blank=True)
  ext = models.CharField(u'分機',max_length=100,null=True,blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.type or ''}"