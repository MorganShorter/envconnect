<template>
  <form @submit.prevent="processForm">
    <form-question-footer
      :previousAnswer="previousAnswer"
      :questionType="question.type"
      :textareaPlaceholder="question.placeholder"
      :textareaValue="textAnswer"
      :numRows="8"
      :focus="true"
      @textareaUpdate="updateAnswer"
    />
  </form>
</template>

<script>
import FormQuestionFooter from '@/components/FormQuestionFooter'

export default {
  name: 'FormQuestionTextarea',

  props: ['question', 'answer', 'previousAnswer'],

  methods: {
    processForm: function () {
      const isEmpty = !this.textAnswer
      this.$emit('submit', [this.textAnswer], isEmpty)
    },
    updateAnswer(value) {
      this.textAnswer = value
    },
  },

  data() {
    return {
      textAnswer: this.answer.answers[0],
    }
  },

  components: {
    FormQuestionFooter,
  },
}
</script>
