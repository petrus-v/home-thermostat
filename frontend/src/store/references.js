import { Device } from "@/models/Device";

export function initData() {
  initDevice();
}

export function initDevice() {
  Device.insert({
    data: [
      { name: "Chaudière", code: "BURNER" },
      { name: "Circulateur", code: "ENGINE" },
    ],
  });
}