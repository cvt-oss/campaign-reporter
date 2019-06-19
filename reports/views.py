import requests
from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .models import Request, Invoice
from .serializers import InputInvoiceSerializer, InvoiceSerializer
from .serializers import RequestSerializer, ImportPdfSerializer


class ExternalServiceError(APIException):
    status_code = 503
    default_detail = 'External service unavailable, try later'
    default_code = 'service_unavailable'


class RequestViewSet(viewsets.ModelViewSet):
    model = Request
    queryset = Request.objects
    serializer_class = RequestSerializer


class InvoiceFilter(filters.FilterSet):
    min_date = filters.DateTimeFilter(field_name="dt_payment", lookup_expr='gte')
    max_date = filters.DateTimeFilter(field_name="dt_payment", lookup_expr='lte')

    class Meta:
        model = Invoice
        fields = ['id', 'min_date', 'max_date']


def get_invoice(invoice_id):
    try:
        return requests.get("%s/api/pdf/%d" % (settings.PDF_ANALYZER_URL, invoice_id)).json()
    except Exception:
        raise ExternalServiceError(detail="PDF analyzer unavailable, try later.")
    '''
    return {
        "accountId": "sampleAccountId",
        "id": 1,
        "invoiceItems": [{
                "campaignName": "CampaignName1",
                "id": 2,
                "price": 1001.86
            }, {
                "campaignName": "CampaignName2",
                "id": 3,
                "price": 201.97
        }],
        "originalFileName": "invoice.pdf",
        "paidOn": "2019-01-19T15:56",
        "referentialNumber": "sampleRefNumber",
        "totalPaid": 101.00,
        "transactionId": "sampleTransactionIda"
    }
    '''


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Invoice import and filtration
    """
    model = Invoice
    queryset = Invoice.objects
    serializer_class = InvoiceSerializer
    filterset_class = InvoiceFilter

    def create(self, request):
        serializer = ImportPdfSerializer(data=request.data)
        if serializer.is_valid():
            invoice_id = serializer.data['invoice_id']
            data = get_invoice(invoice_id)
            try:
                invoice = Invoice.objects.get(transaction_id=data['transactionId'])
            except Invoice.DoesNotExist:
                invoice = None
            serializer = InputInvoiceSerializer(data=data, instance=invoice)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'invoice_id': serializer.instance.pk,
                    'analyzer_invoice_id': invoice_id,
                    'items': len(data['invoiceItems'])
                })
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
