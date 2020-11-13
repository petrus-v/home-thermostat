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
        create_date: "2020-11-12T21:50:35.658031+00:00",
      }),
      "/api/device/relay/BURNER/desired/state": Promise.resolve({
        is_open: true,
        create_date: "2020-11-12T23:12:42.855879",
      }),
      "/api/device/relay/ENGINE/state": Promise.resolve({
        is_open: true,
        create_date: "2020-11-12T23:12:42.855879+05:00",
      }),
      "/api/device/relay/BURNER/state": Promise.resolve({
        is_open: false,
        create_date: "2020-11-12T19:25:32.855879",
      }),
    });
    const departure_uri = `/api/device/thermometer/${global.DEPARTURE}/state`;
    const arrival_uri = `/api/device/thermometer/${global.ARRIVAL}/state`;
    API_RESULTS[departure_uri] = Promise.resolve({
      celsius: 12.3,
      create_date: "2020-11-10T19:25:32.855879",
    });
    API_RESULTS[arrival_uri] = Promise.resolve({
      celsius: 22.8,
      create_date: "2020-10-10T19:25:32.855879",
    });
  });

  it("Testing slider style", async () => {
    const wrapper = shallowMount(Home, {
      store,
      localVue,
    });
    await flushPromises();
    expect(wrapper.vm.sliderType(-1.1, 0, 5, 10)).toBe("is-info");
    expect(wrapper.vm.sliderType(2, 0, 5, 10)).toBe("is-success");
    expect(wrapper.vm.sliderType(7, 0, 5, 10)).toBe("is-warning");
    expect(wrapper.vm.sliderType(11, 0, 5, 10)).toBe("is-danger");
  });

  it("Testing date parser", async () => {
    const wrapper = shallowMount(Home, {
      store,
      localVue,
    });
    await flushPromises();
    expect(wrapper.vm.desiredEngineStateDate).toBe("12/11/2020 à 21:50");
    expect(wrapper.vm.desiredBurnerStateDate).toBe("12/11/2020 à 23:12");
    expect(wrapper.vm.engineStateDate).toBe("12/11/2020 à 18:12");
    expect(wrapper.vm.burnerStateDate).toBe("12/11/2020 à 19:25");
    expect(wrapper.vm.departureDate).toBe("10/11/2020 à 19:25");
    expect(wrapper.vm.arrivalDate).toBe("10/10/2020 à 19:25");
    // // On my FR laptop
    // expect(wrapper.vm.desiredEngineStateDate).toBe("12/11/2020 à 22:50");
    // expect(wrapper.vm.desiredBurnerStateDate).toBe("13/11/2020 à 00:12");
    // expect(wrapper.vm.engineStateDate).toBe("12/11/2020 à 19:12");
    // expect(wrapper.vm.burnerStateDate).toBe("12/11/2020 à 20:25");
    // expect(wrapper.vm.departureDate).toBe("10/11/2020 à 20:25"); // CET
    // expect(wrapper.vm.arrivalDate).toBe("10/10/2020 à 21:25"); // CEST
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
