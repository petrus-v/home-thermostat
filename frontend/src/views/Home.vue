<template>
  <div data-se="home-page">
    <section>
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
          Etat désiré du bruleur
          <b-loading :is-full-page="false" v-model="isDesiredBurnerLoading" :can-cancel="false"></b-loading>
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
          Etat du bruleur
          <b-loading :is-full-page="false" v-model="isBurnerLoading" :can-cancel="false"></b-loading>
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
          Etat désiré du circulateur
          <b-loading :is-full-page="false" v-model="isDesiredEngineLoading" :can-cancel="false"></b-loading>
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
          Etat du circulateur
          <b-loading :is-full-page="false" v-model="isEngineLoading" :can-cancel="false"></b-loading>
        </b-switch>
      </div>
      <div class="buttons">
        <b-button @click="getStates" icon-left="refresh">Rafraîchir</b-button>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
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
  methods: {
    getStates() {
      this.getBurnerState();
      this.getBurnerDesiredState();
      this.getEngineState();
      this.getEngineDesiredState();
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
      const error_state = { is_open: true };
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
