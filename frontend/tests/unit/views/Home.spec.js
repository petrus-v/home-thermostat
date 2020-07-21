import { mount } from "@vue/test-utils";
import Home from "@/views/Home";
import flushPromises from "flush-promises";
const localVue = global.localVue;
const store = global.store;

const API_RESULTS = {
  "/api/device/ENGINE/desired/state": Promise.resolve({ is_open: true }),
  "/api/device/BURNER/desired/state": Promise.resolve({ is_open: true }),
  "/api/device/ENGINE/state": Promise.resolve({ is_open: true }),
  "/api/device/BURNER/state": Promise.resolve({ is_open: false }),
};

global.fetch = jest.fn((api, content) => {
  return Promise.resolve({
    ok: true,
    json: () => API_RESULTS[api],
  });
});

describe("Home", () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  it("mount Home view", async () => {
    const wrapper = mount(Home, {
      store,
      localVue,
    });
    await flushPromises()
    expect(wrapper.element).toMatchSnapshot();
  });
});
