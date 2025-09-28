import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    participant = django_filters.NumberFilter(method="filter_by_participant")
    since = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="gte")
    until = django_filters.IsoDateTimeFilter(field_name="created_at", lookup_expr="lte")
    conversation = django_filters.NumberFilter(field_name="conversation__id", lookup_expr="exact")
    sender = django_filters.NumberFilter(field_name="sender__id", lookup_expr="exact")

    class Meta:
        model = Message
        fields = ["participant", "since", "until", "conversation", "sender"]

    def filter_by_participant(self, queryset, name, value):
        return queryset.filter(conversation__participants__id=value)
