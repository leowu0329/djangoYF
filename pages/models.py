from django.db import models
from django.urls import reverse
from decimal import Decimal, InvalidOperation, DivisionByZero

# Create your models here.


class Cases(models.Model):
  caseNumber=models.CharField(u'案號(*)',max_length=100)
  company=models.CharField(u'所屬公司',max_length=50,null=True,blank=True)
  city=models.CharField(u'縣市',max_length=50,null=True,blank=True)
  township=models.CharField(u'鄉鎮區里',max_length=50,null=True,blank=True)
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

  def fullAddress(self):
    address_parts = [
        self.city,
        self.township,
        self.village,
        self.neighbor,
        self.street,
        self.section,
        self.lane,
        self.alley,
        self.number,
        self.Floor
    ]
    return ''.join(filter(None, address_parts))


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

  def save(self, *args, **kwargs):
    try:
      personal = Decimal(self.holdingPointPersonal or 0)
      total = Decimal(self.holdingPointAll or 0)
      area_m2 = Decimal(self.area or 0)
      if total and area_m2:
        base = (personal / total) * area_m2 * Decimal('0.3025')
        if (self.typeUse or '') == '增建-持分後坪數打對折':
          base = base / Decimal('2')
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
  phone = models.CharField(u'電話', max_length=30)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def __str__(self):
    return f"{self.name} ({self.type})"


class Survey(models.Model):
  cases = models.ForeignKey(Cases, related_name='surveys', on_delete=models.CASCADE, verbose_name=u'案件')
  firstDay = models.CharField(u'初勘日', max_length=100, null=True, blank=True)
  secondDay = models.CharField(u'會勘日', max_length=100, null=True, blank=True)
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
  name = models.CharField(u'人員', max_length=10, null=True, blank=True)
  date = models.CharField(u'日期', max_length=10, null=True, blank=True)
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
    ("無人優購", "無人優購")
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
  transactionDate = models.CharField(u'成交日期', max_length=100, null=True, blank=True)
  floorHeight = models.CharField(u'樓高', max_length=100, null=True, blank=True)
  totalPrice = models.DecimalField(u'總價', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  buildArea = models.DecimalField(u'建坪(坪)', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  subBuildArea = models.DecimalField(u'增建坪數(坪)', default=0, max_digits=10, decimal_places=2, null=True, blank=True)
  unitPrice = models.DecimalField(u'單價', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  calculate = models.DecimalField(u'計算', default=0, max_digits=10, decimal_places=0, null=True, blank=True)
  created = models.DateTimeField(u'建立時間', auto_now=False, auto_now_add=True)
  updated = models.DateTimeField(u'更新時間', auto_now=True, auto_now_add=False)

  def save(self, *args, **kwargs):
    try:
      total_price = Decimal(self.totalPrice or 0)
      build_area = Decimal(self.buildArea or 0)
      sub_build_area = Decimal(self.subBuildArea or 0)
      denominator = build_area + (sub_build_area / Decimal('2'))
      if denominator and denominator != 0:
        # unitPrice = totalPrice / (buildArea + (subBuildArea / 2))
        self.unitPrice = (total_price / denominator).quantize(Decimal('1'))
      else:
        self.unitPrice = Decimal('0')
    except (InvalidOperation, DivisionByZero):
      self.unitPrice = Decimal('0')
    super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.cases.caseNumber} - {self.address or ''}"
