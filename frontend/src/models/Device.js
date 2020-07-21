import { Model } from "@vuex-orm/core";

export class Device extends Model {
  static entity = "devices";
  static primaryKey = 'code'
  static fields() {
    return {
      code: this.string(""),
      name: this.string(""),
    };
  }
}
