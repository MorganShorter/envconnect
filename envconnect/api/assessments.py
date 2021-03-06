# Copyright (c) 2020, DjaoDjin inc.
# see LICENSE.

import logging
from collections import namedtuple

from django.db import connection, transaction
from rest_framework import response as http
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT
from survey.api.sample import (AnswerAPIView, SampleAPIView,
    SampleAnswersAPIView, SampleResetAPIView)
from survey.api.serializers import AnswerSerializer
from survey.models import Answer, EnumeratedQuestions
from survey.utils import get_question_model

from ..mixins import ExcludeDemoSample, ReportMixin
from ..models import Consumption, get_scored_answers
from ..scores import freeze_scores
from ..serializers import AnswerUpdateSerializer


LOGGER = logging.getLogger(__name__)


class AssessmentAnswerAPIView(ExcludeDemoSample, AnswerAPIView):
    """
    Answers about the implementation of a best practice.

    **Tags**: survey

    **Examples

    .. code-block:: http

        POST /api/energy-utility/sample/724bf9648af6420ba79c8a37f962e97e/3/ \
          HTTP/1.1

    .. code-block:: json

        {}

    responds

    .. code-block:: json

        {}
    """
    serializer_class = AnswerSerializer # otherwise API doc is not generated.

    def get_queryset(self):
        # XXX Same as AnswerAPIView but filters only the `default_metric`
        return super(AssessmentAnswerAPIView, self).get_queryset().filter(
            metric=self.question.default_metric)

    def get_http_response(self, serializer,
                     status=HTTP_200_OK, headers=None, first_answer=False):
        #pylint:disable=protected-access,arguments-differ
        scored_answers = get_scored_answers(
            Consumption.objects.get_active_by_accounts(
                self.sample.survey, excludes=self._get_filter_out_testing()),
            self.question.default_metric_id,
            includes=(self.sample,),
            questions=(self.question.pk,))
        with connection.cursor() as cursor:
            cursor.execute(scored_answers, params=None)
            col_headers = cursor.description
            decorated_answer_tuple = namedtuple('DecoratedAnswerTuple',
                [col[0] for col in col_headers])
            decorated_answer = decorated_answer_tuple(*cursor.fetchone())
        data = AnswerUpdateSerializer(context={
            'campaign': self.sample.survey,
            'required': EnumeratedQuestions.objects.filter(
                campaign=self.sample.survey,
                question_id=self.question.pk).first().required
        }).to_representation({
            'consumption':decorated_answer,
            'first': first_answer
        })
        return http.Response(data, status=status, headers=headers)


class AssessmentAPIView(ReportMixin, SampleAPIView):
    """
    Retrieve a subset of datapoints for a sample

    Providing {sample} is a set of datapoints for {interviewee}, returns
    a subset of datapoints whose question starts with a {path} prefix.

    **Tags**: survey

    **Examples**

    .. code-block:: http

         GET /api/supplier-1/sample/0123456789abcdef/ HTTP/1.1

    responds

    .. code-block:: json

        {
            "slug": "0123456789abcdef",
            "account": "supplier-1",
            "created_at": "2020-01-01T00:00:00Z",
            "is_frozen": true,
            "campaign": null,
            "time_spent": null,
        }
    """
    account_url_kwarg = 'interviewee'

    def delete(self, request, *args, **kwargs):
        """
        Reset a subset of datapoints for a sample

        Resets all answers whose question's path starts with a specified prefix.

        **Examples

        .. code-block:: http

            DELETE /api/supplier-1/sample/0123456789abcdef/water-use/ HTTP/1.1
        """
        return self.destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        #pylint:disable=unused-argument
        # We donot call super() because the up-to-date assessment should
        # never be frozen.
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
            data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            freeze_scores(self.sample,
                includes=self.get_included_samples(),
                excludes=self._get_filter_out_testing(),
                collected_by=self.request.user,
                segment_path=self.kwargs.get('path'))
            if self.improvement_sample:
                freeze_scores(self.improvement_sample,
                    includes=self.get_included_samples(), # XXX overriden!
                    excludes=self._get_filter_out_testing(),
                    collected_by=self.request.user)

        return http.Response(serializer.data)


class AssessmentFreezeAPIView(AssessmentAPIView):
    pass


class AssessmentAnswersAPIView(ReportMixin, SampleAnswersAPIView):
    """
    Retrieves measurements or comment to an answer

    **Tags**: survey

    **Examples

    .. code-block:: http

        GET /api/energy-utility/sample/724bf9648af6420ba79c8a37f962e97e/\
3/measures/ HTTP/1.1

    .. code-block:: json

        {}

    responds

    .. code-block:: json

        {}
    """
    account_url_kwarg = 'interviewee'
#    serializer_class = AnswerUpdateSerializer

    def post(self, request, *args, **kwargs):
        """
        Adds a measurement or comment to an answer

        **Tags**: survey

        **Examples

        .. code-block:: http

            POST /api/energy-utility/sample/724bf9648af6420ba79c8a37f962e97e/\
    answers/water-use/target HTTP/1.1

        .. code-block:: json

            {}

        responds

        .. code-block:: json

            {}
        """
        return super(AssessmentAnswersAPIView, self).post(
            request, *args, **kwargs)

    def get_http_response(self, results,
                     status=HTTP_200_OK, headers=None, first_answer=False):

        result = None
        for answer in results:
            if answer.metric_id == answer.question.default_metric_id:
                result = answer
                break
        default_metric_id = answer.question.default_metric_id
        question_pk = answer.question.pk
        questions_pk = (question_pk,)

        #pylint:disable=protected-access,arguments-differ
        planned = None
        implemented = None
        scored_answers = get_scored_answers(
            Consumption.objects.get_active_by_accounts(
                self.sample.survey,
                excludes=self._get_filter_out_testing()),
            default_metric_id,
            includes=(self.sample,),
            questions=questions_pk)
        with connection.cursor() as cursor:
            cursor.execute(scored_answers, params=None)
            col_headers = cursor.description
            decorated_answer_tuple = namedtuple('DecoratedAnswerTuple',
                [col[0] for col in col_headers])
            decorated_answer = decorated_answer_tuple(*cursor.fetchone())
            if decorated_answer.is_planned:
                planned = decorated_answer.is_planned
            else:
                implemented = decorated_answer.implemented

        required = (result.metric_id == result.question.default_metric_id
            and EnumeratedQuestions.objects.filter(
                campaign=self.sample.survey,
                question_id=result.question).first().required)

        setattr(result.question, 'metric',
                str(result.question.default_metric))
        setattr(result.question, 'nb_respondents',
                decorated_answer.nb_respondents)
        setattr(result.question, 'required', required)
        setattr(result.question, 'rank', decorated_answer.rank)
        setattr(result.question, 'rate', decorated_answer.rate)
        setattr(result.question, 'opportunity', decorated_answer.opportunity)

        setattr(result.question, 'implemented', implemented)
        setattr(result.question, 'planned', planned)

        self._expand_choices([result])
        result.first = first_answer
        data = AnswerUpdateSerializer(context={
            'campaign': self.sample.survey,
        }).to_representation(result)
        return http.Response(data, status=status, headers=headers)


class AssessmentResetAPIView(ReportMixin, SampleResetAPIView):

    def post(self, request, *args, **kwargs):
        """
        Reset a subset of datapoints for a sample

        Resets all answers whose question's path starts with a specified prefix.

        **Examples

        .. code-block:: http

            POST /api/supplier-1/sample/0123456789abcdef/reset/water-use/ HTTP/1.1
        """
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        prefix = kwargs.get('path', '')
        if prefix:
            queryset = Answer.objects.filter(
                sample=self.sample,
                question__path__startswith=prefix)
            queryset.delete()
            _, trail = self.breadcrumbs
            segment = trail[0][1] if trail else None
            if segment:
                nb_questions = Consumption.objects.filter(
                    path__startswith=segment).count()
                nb_answers = Answer.objects.filter(sample=self.sample,
                    question__path__startswith=segment).count()
                data = {'nb_answers': nb_answers, 'nb_questions': nb_questions}
                return http.Response(data, status=HTTP_200_OK)
            return http.Response(data, status=HTTP_204_NO_CONTENT)
        return super(AssessmentResetAPIView, self).destroy(
            request, *args, **kwargs)
