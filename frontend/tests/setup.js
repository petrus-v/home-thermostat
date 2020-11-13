import "unfetch/polyfill";
import Buefy from "buefy";
import Vue from "vue";
import Vuex from "vuex";
import { createLocalVue } from "@vue/test-utils";
import Router from "vue-router";
import { store } from "@/store";
import { initData } from "@/store/references";
import { router } from "@/router";

Vue.config.productionTip = false;

// shared localVue
global.localVue = createLocalVue();
global.localVue.use(Buefy);
global.localVue.use(Vuex);
global.localVue.use(Router);
global.store = store;
global.router = router;

global.DEPARTURE = "28-01193a4a4aa2";
global.ARRIVAL = "28-01193a77449f";

initData();
