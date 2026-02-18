import django_filters
from ..models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    issued_on = django_filters.DateFromToRangeFilter()

    provider = django_filters.NumberFilter(field_name="lines__barrel__provider")

    class Meta:
        model = Invoice
        fields = ["invoice_no", "issued_on"]


class ProviderFilter(django_filters.FilterSet):
    # /api/providers/?has_barrels_to_bill=true
    has_barrels_to_bill = django_filters.BooleanFilter(method="filter_has_barrels_to_bill")

    class Meta:
        model = Provider
        fields = ["has_barrels_to_bill"]

    def filter_has_barrels_to_bill(self, queryset, name, value):
        if value is None:
            return queryset

        unbilled = Barrel.objects.filter(provider=OuterRef("pk"), billed=False)
        qs = queryset.annotate(_has_unbilled=Exists(unbilled))
        return qs.filter(_has_unbilled=value)
