# Copyright (c) 2019, DjaoDjin inc.
# see LICENSE.

import six

#pylint:disable=no-name-in-module,import-error,unused-import
from six.moves.urllib.parse import urljoin

try:
    from django.urls import NoReverseMatch, reverse, reverse_lazy
except ImportError: # <= Django 1.10, Python<3.6
    from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy
except ModuleNotFoundError: #pylint:disable=undefined-variable
    # <= Django 1.10, Python>=3.6
    from django.core.urlresolvers import NoReverseMatch, reverse, reverse_lazy
