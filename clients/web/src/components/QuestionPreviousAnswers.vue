<template>
  <v-card outlined class="d-inline-block py-3 px-4 mb-6" v-if="previousAnswer">
    <span class="mr-1">Previous Answer:</span>
    <b>{{ answerText }}</b>
    <p class="text-caption mt-1 mb-0">
      Submitted by {{ previousAnswer.author }} on
      <span v-format-date>{{ previousAnswer.frozen }}</span> in previous
      sustainability assessment.
    </p>
  </v-card>
</template>

<script>
import { MAP_QUESTION_FORM_TYPES } from '@/config/app'
import { formatDate } from '@/directives'

export default {
  name: 'QuestionPreviousAnswers',

  props: ['questionType', 'previousAnswer'],

  computed: {
    answerText() {
      return (
        this.previousAnswer &&
        MAP_QUESTION_FORM_TYPES[this.questionType].render(
          this.previousAnswer.answers
        )
      )
    },
  },

  directives: {
    formatDate,
  },
}
</script>
