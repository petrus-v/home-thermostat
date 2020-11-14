import { shallowMount } from "@vue/test-utils";
import Thermometer from "@/components/Thermometer";

const localVue = global.localVue;
const store = global.store;

describe("Home", () => {
  it("Testing slider style", () => {
    const wrapper = shallowMount(Thermometer, {
      store,
      localVue,
    });
    wrapper.setProps({ value: -1.1, step1: 0, step2: 5, step3: 10 });
    expect(wrapper.vm.sliderType).toBe("is-info");
    wrapper.setProps({ value: 2, step1: 0, step2: 5, step3: 10 });
    expect(wrapper.vm.sliderType).toBe("is-success");
    wrapper.setProps({ value: 7, step1: 0, step2: 5, step3: 10 });
    expect(wrapper.vm.sliderType).toBe("is-warning");
    wrapper.setProps({ value: 11, step1: 0, step2: 5, step3: 10 });
    expect(wrapper.vm.sliderType).toBe("is-danger");
  });

  it("ticksValues", () => {
    const wrapper = shallowMount(Thermometer, {
      store,
      localVue,
    });
    wrapper.setProps({ min: -5, max: 75, tickStep: 5 });

    expect(wrapper.vm.ticksValues).toEqual([
      -5,
      0,
      5,
      10,
      15,
      20,
      25,
      30,
      35,
      40,
      45,
      50,
      55,
      60,
      65,
      70,
      75,
    ]);

    // wrapper.setProps({ min: 10, max: 20, tickStep: 2 });
    // expect(wrapper.vm.ticksValues).toEqual([10, 12, 14, 16, 18, 20]);
  });
});
