import requests

from django.conf import settings
from django.contrib.admin.actions import delete_selected
from django.contrib.admin.sites import site
from django.utils.translation import gettext as _
from django import forms
from django.shortcuts import render, redirect
import object_tools

from reports.models import Invoice
from reports.views import get_invoice, InputInvoiceSerializer

from reports import models

class UploadForm(forms.Form):
    file = forms.FileField(label=_("Invoice in PDF"))

def upload_invoice(pdf_file):
    return requests.post("%s/api/pdf/invoice/process" % settings.PDF_ANALYZER_URL, data="").json()['id']
    #return 1

def import_invoice(data):
    try:
        invoice = Invoice.objects.get(transaction_id=data['transactionId'])
    except Invoice.DoesNotExist:
        invoice = None
    serializer = InputInvoiceSerializer(data=data, instance=invoice)
    if serializer.is_valid():
        serializer.save()
        return serializer.instance
    raise Exception()

class ImportInvoice(object_tools.ObjectTool):
    name = 'import_invoice'
    label = _('Import invoice')

    def view(self, request, extra_context=None):
        #queryset = self.model.objects.all()
        modeladmin = site._registry.get(self.model)
        if request.POST:
            form = UploadForm(request.POST, request.FILES)
            invoice_id = upload_invoice(request.FILES['file'])
            data = get_invoice(invoice_id)
            import_invoice(data)
            if form.is_valid():
                return modeladmin.changelist_view(request)
        else:
            form = UploadForm()
        return render(request, 'admin/import_invoice.html',
                      context={'form': form})

object_tools.tools.register(ImportInvoice, model_class=models.Invoice)
