<template>
  <div data-se="home-page">
    <section>
      <div class="buttons">
        <b-field>
          <b-button @click="getStates" icon-left="refresh">Rafraîchir</b-button>
          <b-select
            v-model="mode.mode"
            placeholder="Select mode"
            v-on:input="onChangeMode"
            :loading="isModeLoading"
            :disabled="isModeLoading"
          >
            <option value="manual">Manuel</option>
            <option value="thermostat">Thermostat</option>
          </b-select>
        </b-field>
      </div>
      <div class="box" v-if="mode.mode === 'thermostat'">
        <h2 class="subtitle">Réglages</h2>
        <b-field label="Température minimale (°C)">
          <b-numberinput
            placeholder="T°C minimale..."
            icon="thermometer"
            step="0.5"
            min-step="0.1"
            v-model="minimalTemperatureState.celsius"
            v-on:input="onChangeMinimalTemperature"
            :loading="isMinimalTemperatureLoading"
            controls-position="compact"
          ></b-numberinput>
        </b-field>
        <b-field label="Confort">
          <b-clockpicker
            placeholder="Début..."
            icon="clock"
            hour-format="24"
            :increment-minutes="5"
            locale="fr-FR"
            :auto-switch="false"
            hours-label="Heures"
            :time-formatter="displayedTime"
            v-model="startTime"
            :loading="isConfortRangeLoading"
            :disabled="isConfortRangeLoading"
            editable
          ></b-clockpicker>
          <b-clockpicker
            placeholder="Fin..."
            icon="clock"
            hour-format="24"
            :increment-minutes="5"
            locale="fr-FR"
            :auto-switch="false"
            hours-label="Heures"
            v-model="endTime"
            :loading="isConfortRangeLoading"
            :disabled="isConfortRangeLoading"
            editable
          ></b-clockpicker>
        </b-field>
        <b-field>
          <b-numberinput
            placeholder="T°C confort..."
            icon="thermometer"
            controls-position="compact"
            v-model="confortCelsius"
            :loading="isConfortRangeLoading"
            :disabled="isConfortRangeLoading"
            :min="minimalTemperatureState.celsius"
            step="0.5"
            min-step="0.1"
          ></b-numberinput>
        </b-field>
      </div>
      <div class="box">
        <h2 class="subtitle">Relais</h2>
        <div class="field">
          <b-switch
            :disabled="mode.mode !== 'manual' || isDesiredBurnerLoading"
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
            :disabled="mode.mode !== 'manual' || isDesiredEngineLoading"
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

        <thermometer
          label="Intérieur"
          :message="livingRoomDate"
          :min="-15"
          :max="50"
          :step1="5"
          :step2="18"
          :step3="22"
          :value="livingRoomState.celsius"
          :loading="isLivingRoomLoading"
        />
        <thermometer
          label="Extérieur"
          :message="outsideDate"
          :min="-15"
          :max="50"
          :step1="0"
          :step2="18"
          :step3="28"
          :value="outsideState.temperature"
          :loading="isOutsideLoading"
        />
        <thermometer
          label="Départ (°C)"
          :message="departureDate"
          :min="-5"
          :max="75"
          :step1="20"
          :step2="40"
          :step3="60"
          :value="departureState.celsius"
          :loading="isDeapartureLoading"
        />
        <thermometer
          label="Retour (°C)"
          :message="arrivalDate"
          :min="-5"
          :max="75"
          :value="arrivalState.celsius"
          :loading="isArrivalLoading"
        />
      </div>

       <div class="box" v-if="mode.mode === 'thermostat'">
        <h2 class="subtitle">Réglages avancés</h2>
        <b-field label="Température Départ Maximum (°C)">
          <b-tooltip>
            <b-numberinput
              placeholder="T°C depart maxi..."
              icon="thermometer"
              step="1"
              min-step="0.1"
              v-model="MaxDepDesiredState.celsius"
              v-on:input="onChangeMaxDepDesired"
              :loading="isMaxDepDesiredLoading"
              controls-position="compact"
            ></b-numberinput>
            <template v-slot:content>
              <p>
                Arrête de chauffer si le tuyau de départ à dépasser cette valeur.
              </p>
            </template>
          </b-tooltip>
        </b-field>
        <b-field label="Température Retour Maximum (°C)">
          <b-tooltip>
            <b-numberinput
              placeholder="T°C retour maxi..."
              icon="thermometer"
              step="1"
              min-step="0.1"
              v-model="MaxRetDesiredState.celsius"
              v-on:input="onChangeMaxRetDesired"
              :loading="isMaxRetDesiredLoading"
              controls-position="compact"
            ></b-numberinput>
            <template v-slot:content>
              <p>
                Arrête de chauffer si le tuyau de retour à dépasser cette valeur.
              </p>
            </template>
          </b-tooltip>
        </b-field>
        <b-field label="Température de retour avant re-chauffe (°C)">
          <b-tooltip>
            <b-numberinput
              placeholder="T°C retour min..."
              icon="thermometer"
              step="1"
              min-step="0.1"
              v-model="MinRetDesiredState.celsius"
              v-on:input="onChangeMinRetDesired"
              :loading="isMinRetDesiredLoading"
              controls-position="compact"
            ></b-numberinput>
            <template v-slot:content>
              <p>
                Si dernirement le tuyaux de retour à atteint le Maximum,
                alors on attend de redescendre en dessous de cette valeur
                avant de rallumer le brûleur. Penser à la latence de la chaudière
                20 minutes env !
              </p>
            </template>
          </b-tooltip>
        </b-field>
        <b-field label="Circulateur: Ecart température(°C)">
          <b-tooltip>
            <b-numberinput
              placeholder="Min diff (retour - salon)..."
              icon="thermometer"
              step="1"
              min-step="0.1"
              v-model="MinDiffDesiredState.celsius"
              v-on:input="onChangeMinDiffDesired"
              :loading="isMinDiffDesiredLoading"
              controls-position="compact"
            ></b-numberinput>
            <template v-slot:content>
              <p>
                Le circulateur est activé si la chaudière a tourné dans les 2 dernières heures.
              </p>
              <p>
                ou si, la différence de température du tuyaux - celle du salon est supérieur à cette valeur.
              </p>
            </template>
          </b-tooltip>
        </b-field>
      </div>
    </section>
  </div>
</template>

<script>
import Thermometer from "@/components/Thermometer";
import debounce from "lodash/debounce";

const defaultRange = { start: null, end: null, celsius: null };
const defaultRelay = { is_open: true };
const defaultThermometer = { celsius: null };
const defaultWeatherStation = { temperature: null, sensor_date: null };

export default {
  name: "Home",
  components: {
    Thermometer
  },
  data() {
    return {
      confortRange: defaultRange,
      isConfortRangeLoading: true,
      mode: { mode: "thermostat" },
      isModeLoading: true,
      minimalTemperatureState: defaultRange,
      isMinimalTemperatureLoading: true,
      livingRoom: global.LIVING,
      livingRoomState: defaultThermometer,
      isLivingRoomLoading: true,
      outside: global.OUTSIDE,
      outsideState: defaultWeatherStation,
      isOutsideLoading: true,
      departure: global.DEPARTURE,
      isDeapartureLoading: true,
      departureState: defaultThermometer,
      arrival: global.ARRIVAL,
      isArrivalLoading: true,
      arrivalState: defaultThermometer,
      isBurnerLoading: true,
      isDesiredBurnerLoading: true,
      burnerState: defaultRelay,
      burnerDesiredState: defaultRelay,
      isEngineLoading: true,
      isDesiredEngineLoading: true,
      engineState: defaultRelay,
      engineDesiredState: defaultRelay,
      maxDepDesired: global.MAX_DEP_DESIRED,
      MaxDepDesiredState: defaultThermometer,
      isMaxDepDesiredLoading: true,
      maxRetDesired: global.MAX_RET_DESIRED,
      MaxRetDesiredState: defaultThermometer,
      isMaxRetDesiredLoading: true,
      minRetDesired: global.MIN_RET_DESIRED,
      MinRetDesiredState: defaultThermometer,
      isMinRetDesiredLoading: true,
      minDiffDesired: global.MIN_DIFF_DESIRED,
      MinDiffDesiredState: defaultThermometer,
      isMinDiffDesiredLoading: true
    };
  },
  computed: {
    confortCelsius: {
      get() {
        return this.confortRange.celsius;
      },
      set(value) {
        this.confortRange.celsius = value;
        this.onChangeConfortRange();
      }
    },
    startTime: {
      get() {
        return this.parseTime(this.confortRange.start);
      },
      set(value) {
        this.confortRange.start = this.dateToStr(value);
        this.onChangeConfortRange();
      }
    },
    endTime: {
      get() {
        return this.parseTime(this.confortRange.end);
      },
      set(value) {
        this.confortRange.end = this.dateToStr(value);
        this.onChangeConfortRange();
      }
    },
    livingRoomDate() {
      return this.parseDate(this.livingRoomState.create_date);
    },
    outsideDate() {
      return this.parseDate(this.outsideState.sensor_date);
    },
    departureDate() {
      return this.parseDate(this.departureState.create_date);
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
    displayedTime(time) {
      return new Intl.DateTimeFormat("fr-FR", {
        hour: "numeric",
        minute: "numeric",
        hour12: undefined,
        timezome: "Europe/Paris"
      }).format(time);
    },
    parseTime(timeStr) {
      var d = new Date();
      if (timeStr !== null && timeStr.length >= 5) {
        const match = timeStr.match(/(\d\d):(\d\d)/);
        d = new Date(Date.UTC(1970, 1, 1, match[1], match[2]));
      }
      return d;
    },
    dateToStr(value) {
      return value.toLocaleTimeString("fr-FR", { timeZone: "UTC" });
    },
    parseDate(dateStr) {
      if (dateStr === undefined || !dateStr) {
        return "";
      }
      if (dateStr.length == 26) {
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
      this.getMode();
      this.getBurnerState();
      this.getBurnerDesiredState();
      this.getEngineState();
      this.getEngineDesiredState();
      this.getDeapartureState();
      this.getArrivalState();
      this.getMinimalRangeState();
      this.getConfortRageState();
      this.getOutSideState();
      this.getLivingRoomState();
      this.getMaxDepDesired();
      this.getMaxRetDesired();
      this.getMinRetDesired();
      this.getMinDiffDesired();
    },
    onChangeMinimalTemperature() {
      this.setMinimalTemperature();
    },
    onChangeConfortRange: debounce(function() {
      this.setConfortRange();
    }, 2000), // 2s
    onChangeMode(newValue) {
      this.setMode(newValue);
    },
    getMode() {
      this.call_api("/api/mode", "GET", "isModeLoading", "mode", null, {
        mode: null
      });
    },
    setMode(modeValue) {
      this.call_api(
        "/api/mode",
        "POST",
        "isModeLoading",
        "mode",
        JSON.stringify({ mode: modeValue }),
        {
          mode: null
        }
      );
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
    getMinimalRangeState() {
      this.call_api(
        "/api/thermostat/range/00",
        "GET",
        "isMinimalTemperatureLoading",
        "minimalTemperatureState",
        null,
        defaultRange
      );
    },
    getConfortRageState() {
      this.call_api(
        "/api/thermostat/range/10",
        "GET",
        "isConfortRangeLoading",
        "confortRange",
        null,
        defaultRange
      );
    },
    setMinimalTemperature() {
      this.call_api(
        "/api/thermostat/range/00",
        "POST",
        "isMinimalTemperatureLoading",
        "minimalTemperatureState",
        JSON.stringify(this.minimalTemperatureState),
        defaultRange
      );
    },
    setConfortRange() {
      this.call_api(
        "/api/thermostat/range/10",
        "POST",
        "isConfortRangeLoading",
        "confortRange",
        JSON.stringify(this.confortRange),
        defaultRange
      );
    },
    getLivingRoomState() {
      this.getOrSetState(
        "GET",
        "thermometer",
        this.livingRoom,
        "isLivingRoomLoading",
        "livingRoomState",
        null
      );
    },
    getOutSideState() {
      this.getOrSetState(
        "GET",
        "weather-station",
        this.outside,
        "isOutsideLoading",
        "outsideState",
        null
      );
    },
    getMaxDepDesired(){
      this.getOrSetState(
        "GET",
        "thermometer",
        this.maxDepDesired,
        "isMaxDepDesiredLoading",
        "MaxDepDesiredState",
        null
      );
    },
    getMaxRetDesired(){
      this.getOrSetState(
        "GET",
        "thermometer",
        this.maxRetDesired,
        "isMaxRetDesiredLoading",
        "MaxRetDesiredState",
        null
      );
    },
    getMinRetDesired(){
      this.getOrSetState(
        "GET",
        "thermometer",
        this.minRetDesired,
        "isMinRetDesiredLoading",
        "MinRetDesiredState",
        null
      );
    },
    getMinDiffDesired(){
      this.getOrSetState(
        "GET",
        "thermometer",
        this.minDiffDesired,
        "isMinDiffDesiredLoading",
        "MinDiffDesiredState",
        null
      );
    },
    onChangeMaxDepDesired(new_value){
      this.getOrSetState(
        "POST",
        "thermometer",
        this.maxDepDesired,
        "isMaxDepDesiredLoading",
        "MaxDepDesiredState",
        JSON.stringify({ celsius: new_value })
      );
    },
    onChangeMaxRetDesired(new_value){
      this.getOrSetState(
        "POST",
        "thermometer",
        this.maxRetDesired,
        "isMaxRetDesiredLoading",
        "MaxRetDesiredState",
        JSON.stringify({ celsius: new_value })
      );
    },
    onChangeMinRetDesired(new_value){
      this.getOrSetState(
        "POST",
        "thermometer",
        this.minRetDesired,
        "isMinRetDesiredLoading",
        "MinRetDesiredState",
        JSON.stringify({ celsius: new_value })
      );
    },
    onChangeMinDiffDesired(new_value){
      this.getOrSetState(
        "POST",
        "thermometer",
        this.minDiffDesired,
        "isMinDiffDesiredLoading",
        "MinDiffDesiredState",
        JSON.stringify({ celsius: new_value })
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
        relay: defaultRelay,
        thermometer: defaultThermometer
      };
      const error_state = defaultStates[device_type];
      this.call_api(
        `/api/device/${device_type}/${device}/state`,
        method,
        loaderName,
        stateName,
        payload,
        error_state
      );
    },
    call_api(uri, method, loaderName, stateName, payload, error_state) {
      this[loaderName] = true;
      let self = this;
      fetch(uri, {
        method: method,
        body: payload,
        headers: {
          "Content-Type": "application/json"
        }
      })
        .then(function(response) {
          if (!response.ok) {
            self[loaderName] = false;
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
          self[loaderName] = false;
          self[stateName] = error_state;
        });
    }
  },
  mounted() {
    this.getStates();
  }
};
</script>
