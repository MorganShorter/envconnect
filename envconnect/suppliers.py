# Copyright (c) 2018, DjaoDjin inc.
# see LICENSE.

from deployutils.helpers import datetime_or_now
from saas.models import Subscription


def get_supplier_managers(account):
    ends_at = datetime_or_now()
    queryset = Subscription.objects.filter(
        ends_at__gt=ends_at, organization=account).select_related(
            'plan__organization').values_list(
            'plan__organization__slug', 'plan__organization__full_name')
    supplier_managers = [{
        'slug': supplier_manager[0], 'printable_name': supplier_manager[1]} for
            supplier_manager in queryset]
    return supplier_managers
