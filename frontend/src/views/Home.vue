<template>
  <div data-se="home-page">
    <section>
      <div class="field">
          <b-switch 
              :disabled="isDesiredBurnerLoading"
              v-on:input="onChangeDesiredBurnerState"
              v-model="burnerDesiredState"
              type='is-warning'
              size="is-large"
              passive-type='is-dark'>
              Etat désiré du bruleur
              <b-loading :is-full-page="false" v-model="isDesiredBurnerLoading" :can-cancel="false">
              </b-loading>
          </b-switch>
          <b-switch 
              :disabled="true"
              v-model="burnerState"
              type='is-warning'
              size="is-large"
              passive-type='is-dark'>
              Etat du bruleur
              <b-loading :is-full-page="false" v-model="isBurnerLoading" :can-cancel="false">
              </b-loading>
          </b-switch>
      </div>
      <div class="field">
          <b-switch 
              :disabled="isDesiredEngineLoading"
              v-on:input="onChangeDesiredEngineState"
              v-model="engineDesiredState"
              type='is-success'
              size="is-large"
              passive-type='is-dark'>
              Etat désiré du circulateur
              <b-loading :is-full-page="false" v-model="isDesiredEngineLoading" :can-cancel="false">
              </b-loading>
          </b-switch>
          <b-switch 
              :disabled="true"
              v-model="engineState"
              type='is-warning'
              size="is-large"
              passive-type='is-dark'>
              Etat du circulateur
              <b-loading :is-full-page="false" v-model="isEngineLoading" :can-cancel="false">
              </b-loading>
          </b-switch>
      </div>
      <div class="buttons">
          <b-button
            @click="getStates"
            icon-left="refresh">
              Rafraîchir
          </b-button>
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
      burnerState: null,
      burnerDesiredState: null,
      isEngineLoading: true,
      isDesiredEngineLoading: true,
      engineState: null,
      engineDesiredState: null,
    }
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
        "BURNER",
        "isBurnerLoading",
        "burnerState",
        null
      );
    },
    onChangeDesiredBurnerState(new_value) {
      this.getOrSetState(
        "POST",
        "BURNER/desired",
        "isDesiredBurnerLoading",
        "burnerDesiredState",
        JSON.stringify({ is_open: !new_value })
      );
      // TODO: something weird happens in backend
      // if(new_value &&  !this.engineDesiredState){
      //   this.onChangeDesiredEngineState(new_value);
      // }
    },
    getBurnerDesiredState() {
      this.getOrSetState(
        "GET",
        "BURNER/desired",
        "isDesiredBurnerLoading",
        "burnerDesiredState",
        null
      );
    },
    getEngineState() {
      this.getOrSetState(
        "GET",
        "ENGINE",
        "isEngineLoading",
        "engineState",
        null
      );
    },
    onChangeDesiredEngineState(new_value) {
      this.getOrSetState(
        "POST",
        "ENGINE/desired",
        "isDesiredEngineLoading",
        "engineDesiredState",
        JSON.stringify({ is_open: !new_value })
      );
    },
    getEngineDesiredState() {
      this.getOrSetState(
        "GET",
        "ENGINE/desired",
        "isDesiredEngineLoading",
        "engineDesiredState",
        null
      );
    },
    getOrSetState(method, device, loaderName, stateName, payload) {
      this[loaderName] = true;
      let self = this;
      fetch(`/api/device/${device}/state`, {
        method: method,
        body: payload,
        headers: { 
          "Content-Type": "application/json"
        }
      })
        .then(function(response) {
          if (!response.ok) {
            self[loaderName] = true;
            self[stateName] = null;
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          if (response.ok) return response.json();
        })
        .then(function(state) {
          self[stateName] = !state.is_open;
          self[loaderName] = false;
        })
        .catch(err => {
          console.error("Error: ", err);
          self[loaderName] = true;
          self[stateName] = null;
        });
    }
  },
  mounted() {
    this.getStates();
  },
};
</script>
