# Copyright (c) 2020, DjaoDjin inc.
# see LICENSE.

from django.conf.urls import url, include
from pages.settings import PATH_RE

from ...api.benchmark import (DisableScorecardAPIView, EnableScorecardAPIView,
    ScoreWeightAPIView)
from ...api.best_practices import (BestPracticeAPIView,
    BestPracticeMirrorAPIView, BestPracticeMoveAPIView,
    EnableContentAPIView, DisableContentAPIView)
from ...api.columns import ColumnAPIView
from ...api.consumption import ConsumptionListAPIView, ConsumptionDetailAPIView


urlpatterns = [
    url(r'^editables/enable(?P<path>%s)/?$' % PATH_RE,
      EnableContentAPIView.as_view(), name="api_enable"),
    url(r'^editables/disable(?P<path>%s)/?$' % PATH_RE,
      DisableContentAPIView.as_view(), name="api_disable"),
    url(r'^editables/scorecard/enable(?P<path>%s)/?$' % PATH_RE,
      EnableScorecardAPIView.as_view(), name="api_scorecard_enable"),
    url(r'^editables/scorecard/disable(?P<path>%s)/?$' % PATH_RE,
      DisableScorecardAPIView.as_view(), name="api_scorecard_disable"),
    url(r'^editables/score(?P<path>%s)/?$' % PATH_RE,
      ScoreWeightAPIView.as_view(), name="api_score"),
    url(r'^editables/consumption/?$',
      ConsumptionListAPIView.as_view(), name="api_consumption_base"),
    url(r'^editables/consumption(?P<path>%s)/?$' % PATH_RE,
      ConsumptionDetailAPIView.as_view(), name="api_consumption"),
    url(r'^editables/detail(?P<path>%s)/?$' % PATH_RE,
      BestPracticeAPIView.as_view(), name="api_detail"),
    url(r'^editables/column(?P<path>%s)/?$' % PATH_RE,
      ColumnAPIView.as_view(), name="api_column"),
    url(r'^editables/attach(?P<path>%s)/?$' % PATH_RE,
      BestPracticeMoveAPIView.as_view(), name='api_move_node'),
    url(r'^editables/mirror(?P<path>%s)/?$' % PATH_RE,
      BestPracticeMirrorAPIView.as_view(), name='api_mirror_node'),
    url(r'^', include('pages.urls.api.editables')),
]
