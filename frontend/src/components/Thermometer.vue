<template>
  <b-field :label="label" :message="message">
    <b-slider
      :min="min"
      :max="max"
      ticks
      disabled
      indicator
      :value="value"
      :type="sliderType"
      :tooltip-type="sliderType"
    >
      <template v-for="val in ticksValues">
        <b-slider-tick :value="val" :key="'tick-' + val">{{ val }}</b-slider-tick>
      </template>
    </b-slider>
    <b-loading :is-full-page="false" :active="loading" :can-cancel="false"></b-loading>
  </b-field>
</template>

<script>
export default {
  props: {
    label: String,
    message: String,
    value: Number,
    loading: {
      type: Boolean,
      default: false
    },
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      default: 100
    },
    tickStep: {
      type: Number,
      default: 5
    },
    step1: {
      type: Number,
      default: 25
    },
    step2: {
      type: Number,
      default: 50
    },
    step3: {
      type: Number,
      default: 75
    }
  },
  data() {
    return {};
  },
  computed: {
    ticksValues() {
      return Array.from(
        { length: (this.max - this.min) / this.tickStep + 1 },
        (_, i) => i * this.tickStep + this.min
      );
    },
    sliderType() {
      if (this.value > this.step2 && this.value < this.step3) {
        return "is-warning";
      } else if (this.value >= this.step3) {
        return "is-danger";
      } else if (this.value <= this.step1) {
        return "is-info";
      }
      return "is-success";
    }
  },
  method: {}
};
</script>
