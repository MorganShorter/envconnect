<template>
  <fragment>
    <question-previous-answers
      :questionType="questionType"
      :previousAnswer="previousAnswer"
    />
    <v-textarea
      :placeholder="textareaPlaceholder"
      v-model="textarea"
      hide-details="auto"
      auto-grow
      outlined
      :rows="numRows"
      row-height="16"
      :autofocus="focus"
      @input="$emit('textareaUpdate', textarea)"
    ></v-textarea>
    <div class="mt-4 text-right">
      <button-primary type="submit" display="inline">
        <span>Save and Continue</span>
        <v-icon class="ml-2" small color="white">mdi-arrow-right</v-icon>
      </button-primary>
    </div>
  </fragment>
</template>

<script>
import { Fragment } from 'vue-fragment'
import ButtonPrimary from '@/components/ButtonPrimary'
import QuestionPreviousAnswers from '@/components/QuestionPreviousAnswers'

export default {
  name: 'FormQuestionFooter',

  props: {
    focus: {
      type: Boolean,
      default: false,
    },
    numRows: {
      type: Number,
      default: 2,
    },
    previousAnswer: {
      type: Object, // Answer
      default: null,
    },
    questionType: {
      type: String,
      required: true,
    },
    textareaPlaceholder: {
      type: String,
      required: true,
    },
    textareaValue: {
      type: String,
    },
  },

  data() {
    return {
      textarea: this.textareaValue,
    }
  },

  components: {
    ButtonPrimary,
    Fragment,
    QuestionPreviousAnswers,
  },
}
</script>
