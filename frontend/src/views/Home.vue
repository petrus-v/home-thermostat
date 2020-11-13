<template>
  <div data-se="home-page">
    <section>
      <div class="buttons">
        <b-button @click="getStates" icon-left="refresh">Rafraîchir</b-button>
      </div>
      <div class="box">
        <h2 class="subtitle">Relais</h2>
        <div class="field">
          <b-switch
            :disabled="isDesiredBurnerLoading"
            v-on:input="onChangeDesiredBurnerState"
            v-model="burnerDesiredState.is_open"
            :true-value="false"
            :false-value="true"
            type="is-success"
            size="is-large"
            passive-type="is-dark"
            name="switch-desired-burner-state"
          >
            <p>Etat désiré du bruleur</p>
            <b-loading :is-full-page="false" v-model="isDesiredBurnerLoading" :can-cancel="false"></b-loading>
            <span class="is-size-6">{{ desiredBurnerStateDate }}</span>
          </b-switch>
          <b-switch
            :disabled="true"
            v-model="burnerState.is_open"
            :true-value="false"
            :false-value="true"
            type="is-warning"
            size="is-large"
            passive-type="is-dark"
          >
            <p>Etat du bruleur</p>
            <b-loading :is-full-page="false" v-model="isBurnerLoading" :can-cancel="false"></b-loading>
            <span class="is-size-6">{{ burnerStateDate }}</span>
          </b-switch>
        </div>
        <div class="field">
          <b-switch
            :disabled="isDesiredEngineLoading"
            v-on:input="onChangeDesiredEngineState"
            v-model="engineDesiredState.is_open"
            :true-value="false"
            :false-value="true"
            type="is-success"
            size="is-large"
            passive-type="is-dark"
            name="switch-desired-engine-state"
          >
            <p>Etat désiré du circulateur</p>
            <b-loading :is-full-page="false" v-model="isDesiredEngineLoading" :can-cancel="false"></b-loading>
            <span class="is-size-6">{{ desiredEngineStateDate }}</span>
          </b-switch>
          <b-switch
            :disabled="true"
            v-model="engineState.is_open"
            :true-value="false"
            :false-value="true"
            type="is-warning"
            size="is-large"
            passive-type="is-dark"
          >
            <p>Etat du circulateur</p>
            <b-loading :is-full-page="false" v-model="isEngineLoading" :can-cancel="false"></b-loading>
            <span class="is-size-6">{{ engineStateDate }}</span>
          </b-switch>
        </div>
      </div>

      <div class="box">
        <h2 class="subtitle">Températures</h2>

        <b-field label="Départ (°C)" :message="departureDate">
          <b-slider
            :min="-5"
            :max="75"
            ticks
            disabled
            indicator
            v-model="departureState.celsius"
            :type="departureSliderType"
            :tooltip-type="departureSliderType"
          >
            <template v-for="val in Array.from({length: 17}, (_, i) => i * 5 - 5)">
              <b-slider-tick :value="val" :key="'d' + val">{{ val }}</b-slider-tick>
            </template>
          </b-slider>
          <b-loading :is-full-page="false" v-model="isDeapartureLoading" :can-cancel="false"></b-loading>
        </b-field>
        <b-field label="Retour (°C)" :message="arrivalDate">
          <b-slider
            :min="-5"
            :max="75"
            ticks
            disabled
            indicator
            v-model="arrivalState.celsius"
            :type="arrivalSliderType"
            :tooltip-type="arrivalSliderType"
          >
            <template v-for="val in Array.from({length: 17}, (_, i) => i * 5 - 5)">
              <b-slider-tick :value="val" :key="'a' + val">{{ val }}</b-slider-tick>
            </template>
          </b-slider>
          <b-loading :is-full-page="false" v-model="isArrivalLoading" :can-cancel="false"></b-loading>
        </b-field>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      departure: global.DEPARTURE,
      isDeapartureLoading: true,
      departureState: { celsius: null },
      arrival: global.ARRIVAL,
      isArrivalLoading: true,
      arrivalState: { celsius: null },
      isBurnerLoading: true,
      isDesiredBurnerLoading: true,
      burnerState: { is_open: true },
      burnerDesiredState: { is_open: true },
      isEngineLoading: true,
      isDesiredEngineLoading: true,
      engineState: { is_open: true },
      engineDesiredState: { is_open: true }
    };
  },
  computed: {
    departureSliderType() {
      return this.sliderType(this.departureState.celsius, 0, 25, 50);
    },
    departureDate() {
      return this.parseDate(this.departureState.create_date);
    },
    arrivalSliderType() {
      return this.sliderType(this.arrivalState.celsius, 0, 25, 50);
    },
    arrivalDate() {
      return this.parseDate(this.arrivalState.create_date);
    },
    desiredBurnerStateDate() {
      return this.parseDate(this.burnerDesiredState.create_date);
    },
    burnerStateDate() {
      return this.parseDate(this.burnerState.create_date);
    },
    desiredEngineStateDate() {
      return this.parseDate(this.engineDesiredState.create_date);
    },
    engineStateDate() {
      return this.parseDate(this.engineState.create_date);
    }
  },
  methods: {
    sliderType(celsius, b1, b2, b3) {
      if (celsius > b2 && celsius < b3) {
        return "is-warning";
      } else if (celsius >= b3) {
        return "is-danger";
      } else if (celsius <= b1) {
        return "is-info";
      }
      return "is-success";
    },
    parseDate(dateStr) {
      if (dateStr === undefined || !dateStr) {
        return "";
      }
      if (dateStr.length <= 26) {
        dateStr = dateStr.concat("+00:00");
      }

      const date = new Date(Date.parse(dateStr));
      return new Intl.DateTimeFormat("fr-FR", {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
        second: undefined
      }).format(date);
    },
    getStates() {
      this.getBurnerState();
      this.getBurnerDesiredState();
      this.getEngineState();
      this.getEngineDesiredState();
      this.getDeapartureState();
      this.getArrivalState();
    },
    getDeapartureState() {
      this.getOrSetState(
        "GET",
        "thermometer",
        this.departure,
        "isDeapartureLoading",
        "departureState",
        null
      );
    },
    getArrivalState() {
      this.getOrSetState(
        "GET",
        "thermometer",
        this.arrival,
        "isArrivalLoading",
        "arrivalState",
        null
      );
    },
    getBurnerState() {
      this.getOrSetState(
        "GET",
        "relay",
        "BURNER",
        "isBurnerLoading",
        "burnerState",
        null
      );
    },
    onChangeDesiredBurnerState(new_value) {
      this.getOrSetState(
        "POST",
        "relay",
        "BURNER/desired",
        "isDesiredBurnerLoading",
        "burnerDesiredState",
        JSON.stringify({ is_open: new_value })
      );
      if (!new_value && this.engineDesiredState.is_open) {
        this.onChangeDesiredEngineState(new_value);
      }
    },
    getBurnerDesiredState() {
      this.getOrSetState(
        "GET",
        "relay",
        "BURNER/desired",
        "isDesiredBurnerLoading",
        "burnerDesiredState",
        null
      );
    },
    getEngineState() {
      this.getOrSetState(
        "GET",
        "relay",
        "ENGINE",
        "isEngineLoading",
        "engineState",
        null
      );
    },
    onChangeDesiredEngineState(new_value) {
      this.getOrSetState(
        "POST",
        "relay",
        "ENGINE/desired",
        "isDesiredEngineLoading",
        "engineDesiredState",
        JSON.stringify({ is_open: new_value })
      );
    },
    getEngineDesiredState() {
      this.getOrSetState(
        "GET",
        "relay",
        "ENGINE/desired",
        "isDesiredEngineLoading",
        "engineDesiredState",
        null
      );
    },
    getOrSetState(method, device_type, device, loaderName, stateName, payload) {
      const defaultStates = {
        relay: { is_open: true },
        thermometer: { celsius: null }
      };
      const error_state = defaultStates[device_type];
      this[loaderName] = true;
      let self = this;
      fetch(`/api/device/${device_type}/${device}/state`, {
        method: method,
        body: payload,
        headers: {
          "Content-Type": "application/json"
        }
      })
        .then(function(response) {
          if (!response.ok) {
            self[loaderName] = true;
            self[stateName] = error_state;
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          if (response.ok) return response.json();
        })
        .then(function(state) {
          self[stateName] = state;
          self[loaderName] = false;
        })
        .catch(err => {
          console.error("Error: ", err);
          self[loaderName] = true;
          self[stateName] = error_state;
        });
    }
  },
  mounted() {
    this.getStates();
  }
};
</script>
