from django import template

register = template.Library()


@register.simple_tag
def has_active_filters(filterset):
    if not filterset.is_bound:
        return False

    # Get filter field names from the filterset
    filter_fields = set(filterset.filters.keys())

    # Check if any filter field has a non-empty value in the data
    for field_name in filter_fields:
        value = filterset.data.get(field_name)
        if value not in (None, "", []):
            return True

    return False
