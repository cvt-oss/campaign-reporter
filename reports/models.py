from django.db import models
from django.contrib.postgres.search import TrigramSimilarity


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
    approved = models.BooleanField(default=False)
    dt_approved = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return 'Request: %d' % self.id

    class Meta:
        ordering = ('id',)


class Invoice(models.Model):
    transaction_id = models.CharField(max_length=40)
    dt_payment = models.DateTimeField()
    total = models.FloatField(default=0)

    def __str__(self):
        return self.transaction_id

    class Meta:
        ordering = ('transaction_id',)


class Campaign(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=100)
    price = models.FloatField(default=0)
    request = models.OneToOneField(Request, on_delete=models.CASCADE, blank=True, null=True)

    def requests(self):
        """
        Campaign is already linked (manually, confirmed) to request
        or
        we can filter by:
           - approved = True
           - dt_approved < paid, dt_start
           - text ~ name
        """
        if self.request:
            return [{'approved': True, 'id': self.request.id}]

        return Request.objects.filter(
            approved=True,
            dt_approved__lte=self.invoice.dt_payment,
            dt_start__lte=self.invoice.dt_payment,
            campaign__isnull=True
        ).annotate(
            similarity=TrigramSimilarity('text', self.name)
        ).filter(
            similarity__gt=0.3
        ).order_by('-similarity').values('id', 'similarity')[:10]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        unique_together = ('invoice', 'name')
