import { mount, shallowMount } from "@vue/test-utils";
import Home from "@/views/Home";
import flushPromises from "flush-promises";
const localVue = global.localVue;
const store = global.store;

const API_RESULTS = {};

global.fetch = jest.fn((api, content) => {
  return Promise.resolve({
    ok: true,
    json: () => API_RESULTS[api],
  });
});

describe("Home", () => {
  beforeEach(() => {
    fetch.mockClear();
    Object.assign(API_RESULTS, {
      "/api/device/relay/ENGINE/desired/state": Promise.resolve({
        is_open: true,
      }),
      "/api/device/relay/BURNER/desired/state": Promise.resolve({
        is_open: true,
      }),
      "/api/device/relay/ENGINE/state": Promise.resolve({ is_open: true }),
      "/api/device/relay/BURNER/state": Promise.resolve({ is_open: false }),
    });
  });

  it("mount Home view", async () => {
    const wrapper = mount(Home, {
      store,
      localVue,
    });
    await flushPromises();
    expect(wrapper.element).toMatchSnapshot();
  });

  it("make sure it turn on engine if burner is turning on", async () => {
    API_RESULTS["/api/device/relay/BURNER/state"] = Promise.resolve({
      is_open: true,
    });
    const wrapper = shallowMount(Home, {
      store,
      localVue,
    });
    await flushPromises();
    expect(wrapper.vm.burnerDesiredState.is_open).toBe(true);
    expect(wrapper.vm.engineDesiredState.is_open).toBe(true);

    API_RESULTS["/api/device/relay/ENGINE/desired/state"] = Promise.resolve({
      is_open: false,
    });
    API_RESULTS["/api/device/relay/BURNER/desired/state"] = Promise.resolve({
      is_open: false,
    });
    wrapper.vm.onChangeDesiredBurnerState(false);
    await flushPromises();
    expect(wrapper.vm.burnerDesiredState.is_open).toBe(false);
    expect(wrapper.vm.engineDesiredState.is_open).toBe(false);
  });
});
