import Vue from "vue";
import App from "@/App.vue";
import Buefy from "buefy";
import "buefy/dist/buefy.css";
import router from "@/router";
import store from "@/store";
import { initData } from "@/store/references";
Vue.config.productionTip = false;
Vue.use(Buefy, {
  defaultFieldLabelPosition: "on-border",
});

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");

initData();
