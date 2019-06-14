from django.contrib import admin

from .models import Code, Section, Request, Invoice, InvoiceRow, Campaign

admin.site.register(Code)
admin.site.register(Section)
admin.site.register(Request)

class InvoiceRowAdmin(admin.TabularInline):
    model = InvoiceRow
    extra = 1

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'dt_payment', 'total')
    date_hierarchy = 'dt_payment'
    inlines = [InvoiceRowAdmin]
admin.site.register(Invoice, InvoiceAdmin)

class InvoiceRowAdminCampaign(admin.TabularInline):
    model = InvoiceRow
    max_num = 0
    min_num = 0

class CampaignAdmin(admin.ModelAdmin):
    inlines = [InvoiceRowAdminCampaign]
admin.site.register(Campaign, CampaignAdmin)
