import django_filters
from ..models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    issued_on = django_filters.DateFromToRangeFilter()

    provider = django_filters.NumberFilter(field_name="lines__barrel__provider")

    class Meta:
        model = Invoice
        fields = ["invoice_no", "issued_on", "provider"]