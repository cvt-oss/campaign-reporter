from django.db import models

class Code(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', 'active')

class Section(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', 'active')

class Request(models.Model):
    profile = models.CharField(max_length=100, blank=True)
    link = models.URLField(blank=True)
    text = models.TextField(blank=True)
    dt_start = models.DateField(blank=True, null=True)
    dt_end = models.DateField(blank=True, null=True)
    budget = models.PositiveIntegerField(default=0)
    code = models.ForeignKey(Code, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    target_group = models.TextField(blank=True)
    note = models.TextField(blank=True)
    email = models.EmailField()

    def __str__(self):
        return 'Request: %d' % self.id

    class Meta:
        ordering = ('id',)

class Invoice(models.Model):
    transaction_id = models.CharField(max_length=40)
    dt_payment = models.DateTimeField()
    total = models.FloatField()

    def __str__(self):
        return self.transaction_id

    class Meta:
        ordering = ('transaction_id',)

class Campaign(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class InvoiceRow(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    displays = models.PositiveIntegerField()
    price = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('invoice', 'campaign', 'name')
