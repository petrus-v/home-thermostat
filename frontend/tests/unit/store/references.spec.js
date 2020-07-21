import { Device } from "@/models/Device";

describe("References", () => {
  it("query intgrations", () => {
    let device = Device.query();
    test = device.get();
    expect(test.length).toBe(2);
  });
});
