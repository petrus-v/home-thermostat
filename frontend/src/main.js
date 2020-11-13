import Vue from "vue";
import App from "@/App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import router from "@/router";
import store from "@/store";
import { initData } from "@/store/references";
Vue.config.productionTip = false;
Vue.use(Buefy, {
  // defaultFieldLabelPosition: "on-border",
});

// departure: "28-01193a4a4aa2",
// arrival: "28-01193a77449f",
global.DEPARTURE = "28-01193a4a4aa2";
global.ARRIVAL = "28-01193a77449f";

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");

initData();
