import Vue from "vue";
import App from "@/App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import router from "@/router";
import store from "@/store";
import { initData } from "@/store/references";
Vue.config.productionTip = false;
Vue.use(Buefy, {
  defaultLocale: "fr-FR",
  // defaultFieldLabelPosition: "on-border",
});

// departure: "28-01193a4a4aa2",
// arrival: "28-01193a77449f",
global.DEPARTURE = "28-01193a4a4aa2";
global.ARRIVAL = "28-01193a77449f";
global.LIVING = "28-01193a44fa4c";
global.OUTSIDE = "FW5282";


global.MAX_DEP_DESIRED = "max-depart"
global.MAX_RET_DESIRED = "max-return"
global.MIN_RET_DESIRED = "min-return"
global.MIN_DIFF_DESIRED = "min-diff-engine"


new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");

initData();
