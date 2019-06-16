from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.search import TrigramSimilarity
from django.utils.translation import gettext as _


class Code(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    active = models.BooleanField(default=True, help_text=_('Show in dialogs'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', 'active')
        verbose_name = _('Project code')


class Section(models.Model):
    name = models.CharField(max_length=10, primary_key=True)
    active = models.BooleanField(default=True, help_text=_('Show in dialogs'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name', 'active')
        verbose_name = _('Project section')


class Request(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    dt_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'), editable=False)
    profile = models.CharField(max_length=100, blank=True)
    link = models.URLField(blank=True, verbose_name=_('URL link'), help_text=_('URL link to paid post'))
    text = models.TextField(blank=True, help_text=_('Text of the post'))
    dt_start = models.DateField(blank=True, null=True, verbose_name=_('Start of campaign'))
    dt_end = models.DateField(blank=True, null=True, verbose_name=_('End of campaign'))
    budget = models.PositiveIntegerField(default=0, help_text=_('Expected budget'))
    code = models.ForeignKey(Code, on_delete=models.CASCADE, help_text=_('Project code'))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, help_text=_('Project section'))
    target_group = models.TextField(blank=True, help_text=_('Describe your target audience.'))
    note = models.TextField(blank=True, help_text=_('Anything else'))
    email = models.EmailField(verbose_name=_('E-mail'), help_text=_('Contat e-mail'))
    approved = models.BooleanField(default=False, help_text=_('Approved by manager'))
    dt_approved = models.DateTimeField(blank=True, null=True, verbose_name=_('Approval date'))

    def shortened_text(self):
        if len(self.text) < 28:
            return self.text
        else:
            return "%s..." % self.text[:25]

    def __str__(self):
        return '%d: %s' % (self.id, self.shortened_text())

    class Meta:
        ordering = ('id',)


class Invoice(models.Model):
    transaction_id = models.CharField(verbose_name=_('Transaction ID'), max_length=40)
    dt_payment = models.DateTimeField(verbose_name=_('Payment date'), db_index=True)
    total = models.FloatField(default=0, verbose_name=_('Total price'))

    def get_rows(self):
        """
        Return rows suitable for export to table
        """
        rows = []
        for c in self.campaigns.all():
            rows.append([self.transaction_id, c.name, c.price, c.request])
        return rows

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
        verbose_name = _('Campaign in invoice')
        verbose_name_plural = _('Campaigns in invoice')
