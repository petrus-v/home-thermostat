import Vue from "vue";
import Vuex from "vuex";
import VuexORM from "@vuex-orm/core";
import {
  Device,
} from "@/models/Device";

Vue.use(Vuex);
// Create a new instance of Database.
const database = new VuexORM.Database();

// Register Models to Database.
database.register(Device);

export default new Vuex.Store({
  plugins: [VuexORM.install(database)],
  state: {},
  mutations: {},
  actions: {},
  modules: {},
});
