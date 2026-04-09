"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  BLE_SERVICES,
  BLE_CHARACTERISTICS,
  CadenceCalculator,
  parseHeartRate,
  parseCyclingPower,
  parseCSCMeasurement,
  parseIndoorBikeData,
  ftmsRequestControl,
  ftmsStartOrResume,
  ftmsSetTargetPower,
  ftmsStop,
  isBluetoothSupported,
  type DeviceType,
} from "@/lib/bluetooth";

interface DeviceConnection {
  device: BluetoothDevice;
  server: BluetoothRemoteGATTServer;
}

interface BluetoothDeviceState {
  connected: boolean;
  name: string | null;
  battery?: number;
}

export interface BluetoothState {
  isSupported: boolean;
  heartRate: BluetoothDeviceState & { value: number | null };
  power: BluetoothDeviceState & { value: number | null };
  cadence: BluetoothDeviceState & { value: number | null };
  trainer: BluetoothDeviceState & {
    ergMode: boolean;
    targetPower: number | null;
  };
}

export interface BluetoothActions {
  connectHeartRate: () => Promise<void>;
  connectPower: () => Promise<void>;
  connectCadence: () => Promise<void>;
  connectTrainer: () => Promise<void>;
  disconnectDevice: (type: DeviceType) => void;
  setTargetPower: (watts: number) => Promise<void>;
  stopTrainer: () => Promise<void>;
  disconnectAll: () => void;
}

export function useBluetooth(): [BluetoothState, BluetoothActions] {
  const [hrState, setHrState] = useState<BluetoothState["heartRate"]>({
    connected: false,
    name: null,
    value: null,
  });
  const [powerState, setPowerState] = useState<BluetoothState["power"]>({
    connected: false,
    name: null,
    value: null,
  });
  const [cadenceState, setCadenceState] = useState<BluetoothState["cadence"]>({
    connected: false,
    name: null,
    value: null,
  });
  const [trainerState, setTrainerState] = useState<BluetoothState["trainer"]>({
    connected: false,
    name: null,
    ergMode: false,
    targetPower: null,
  });

  const hrConnection = useRef<DeviceConnection | null>(null);
  const powerConnection = useRef<DeviceConnection | null>(null);
  const cadenceConnection = useRef<DeviceConnection | null>(null);
  const trainerConnection = useRef<DeviceConnection | null>(null);
  const trainerControlPoint =
    useRef<BluetoothRemoteGATTCharacteristic | null>(null);
  const cadenceCalc = useRef(new CadenceCalculator());
  const powerCadenceCalc = useRef(new CadenceCalculator());

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      [hrConnection, powerConnection, cadenceConnection, trainerConnection].forEach(
        (ref) => {
          if (ref.current?.server.connected) {
            ref.current.server.disconnect();
          }
        }
      );
    };
  }, []);

  const handleDisconnect = useCallback(
    (type: DeviceType) => () => {
      switch (type) {
        case "heartRate":
          setHrState({ connected: false, name: null, value: null });
          hrConnection.current = null;
          break;
        case "power":
          setPowerState({ connected: false, name: null, value: null });
          powerConnection.current = null;
          powerCadenceCalc.current.reset();
          break;
        case "cadence":
          setCadenceState({ connected: false, name: null, value: null });
          cadenceConnection.current = null;
          cadenceCalc.current.reset();
          break;
        case "trainer":
          setTrainerState({
            connected: false,
            name: null,
            ergMode: false,
            targetPower: null,
          });
          trainerConnection.current = null;
          trainerControlPoint.current = null;
          // Clear trainer-derived sensor readings
          if (!powerConnection.current) {
            setPowerState({ connected: false, name: null, value: null });
          }
          if (!cadenceConnection.current) {
            setCadenceState({ connected: false, name: null, value: null });
          }
          if (!hrConnection.current) {
            setHrState({ connected: false, name: null, value: null });
          }
          break;
      }
    },
    []
  );

  const connectHeartRate = useCallback(async () => {
    if (!isBluetoothSupported()) return;

    const device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [BLE_SERVICES.heartRate] }],
    });

    device.addEventListener(
      "gattserverdisconnected",
      handleDisconnect("heartRate")
    );

    const server = await device.gatt!.connect();
    hrConnection.current = { device, server };

    const service = await server.getPrimaryService(BLE_SERVICES.heartRate);
    const char = await service.getCharacteristic(
      BLE_CHARACTERISTICS.heartRateMeasurement
    );

    await char.startNotifications();
    char.addEventListener("characteristicvaluechanged", (e) => {
      const target = e.target as BluetoothRemoteGATTCharacteristic;
      if (!target.value) return;
      const data = parseHeartRate(target.value);
      setHrState((prev) => ({
        ...prev,
        connected: true,
        name: device.name || "HR Monitor",
        value: data.heartRate,
      }));
    });

    setHrState((prev) => ({
      ...prev,
      connected: true,
      name: device.name || "HR Monitor",
    }));
  }, [handleDisconnect]);

  const connectPower = useCallback(async () => {
    if (!isBluetoothSupported()) return;

    const device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [BLE_SERVICES.cyclingPower] }],
    });

    device.addEventListener(
      "gattserverdisconnected",
      handleDisconnect("power")
    );

    const server = await device.gatt!.connect();
    powerConnection.current = { device, server };

    const service = await server.getPrimaryService(BLE_SERVICES.cyclingPower);
    const char = await service.getCharacteristic(
      BLE_CHARACTERISTICS.cyclingPowerMeasurement
    );

    powerCadenceCalc.current.reset();

    await char.startNotifications();
    char.addEventListener("characteristicvaluechanged", (e) => {
      const target = e.target as BluetoothRemoteGATTCharacteristic;
      if (!target.value) return;
      const data = parseCyclingPower(target.value);
      setPowerState((prev) => ({
        ...prev,
        connected: true,
        name: device.name || "Power Meter",
        value: data.instantaneousPower,
      }));

      // Also extract cadence from power meter if available and no separate cadence sensor
      if (
        data.crankRevolutions !== undefined &&
        data.lastCrankEventTime !== undefined
      ) {
        const rpm = powerCadenceCalc.current.calculate(
          data.crankRevolutions,
          data.lastCrankEventTime,
          2048 // Power meter uses 1/2048s resolution
        );
        if (rpm !== null && !cadenceConnection.current) {
          setCadenceState((prev) => ({
            ...prev,
            value: rpm,
            // Don't set connected - it's derived from power meter
          }));
        }
      }
    });

    setPowerState((prev) => ({
      ...prev,
      connected: true,
      name: device.name || "Power Meter",
    }));
  }, [handleDisconnect]);

  const connectCadence = useCallback(async () => {
    if (!isBluetoothSupported()) return;

    const device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [BLE_SERVICES.cyclingSpeedCadence] }],
    });

    device.addEventListener(
      "gattserverdisconnected",
      handleDisconnect("cadence")
    );

    const server = await device.gatt!.connect();
    cadenceConnection.current = { device, server };

    const service = await server.getPrimaryService(
      BLE_SERVICES.cyclingSpeedCadence
    );
    const char = await service.getCharacteristic(
      BLE_CHARACTERISTICS.cscMeasurement
    );

    cadenceCalc.current.reset();

    await char.startNotifications();
    char.addEventListener("characteristicvaluechanged", (e) => {
      const target = e.target as BluetoothRemoteGATTCharacteristic;
      if (!target.value) return;
      const data = parseCSCMeasurement(target.value);

      if (
        data.crankRevolutions !== undefined &&
        data.lastCrankEventTime !== undefined
      ) {
        const rpm = cadenceCalc.current.calculate(
          data.crankRevolutions,
          data.lastCrankEventTime,
          1024
        );
        if (rpm !== null) {
          setCadenceState((prev) => ({
            ...prev,
            connected: true,
            name: device.name || "Cadence Sensor",
            value: rpm,
          }));
        }
      }
    });

    setCadenceState((prev) => ({
      ...prev,
      connected: true,
      name: device.name || "Cadence Sensor",
    }));
  }, [handleDisconnect]);

  const connectTrainer = useCallback(async () => {
    if (!isBluetoothSupported()) return;

    const device = await navigator.bluetooth.requestDevice({
      filters: [{ services: [BLE_SERVICES.fitnessMachine] }],
      optionalServices: [BLE_SERVICES.heartRate],
    });

    device.addEventListener(
      "gattserverdisconnected",
      handleDisconnect("trainer")
    );

    const server = await device.gatt!.connect();
    trainerConnection.current = { device, server };

    const service = await server.getPrimaryService(BLE_SERVICES.fitnessMachine);

    // Subscribe to Indoor Bike Data
    try {
      const bikeData = await service.getCharacteristic(
        BLE_CHARACTERISTICS.indoorBikeData
      );
      await bikeData.startNotifications();
      bikeData.addEventListener("characteristicvaluechanged", (e) => {
        const target = e.target as BluetoothRemoteGATTCharacteristic;
        if (!target.value) return;
        const data = parseIndoorBikeData(target.value);

        // Update power/cadence/HR from trainer if no dedicated sensor
        const trainerName = device.name || "Smart Trainer";
        if (data.power !== undefined && !powerConnection.current) {
          setPowerState((prev) => ({
            ...prev,
            connected: true,
            name: prev.name || `${trainerName} (power)`,
            value: data.power!,
          }));
        }
        if (data.cadence !== undefined && !cadenceConnection.current) {
          setCadenceState((prev) => ({
            ...prev,
            connected: true,
            name: prev.name || `${trainerName} (cadence)`,
            value: data.cadence!,
          }));
        }
        if (data.heartRate !== undefined && !hrConnection.current) {
          setHrState((prev) => ({
            ...prev,
            connected: true,
            name: prev.name || `${trainerName} (HR)`,
            value: data.heartRate!,
          }));
        }
      });
    } catch {
      // Some trainers don't support Indoor Bike Data
    }

    // Get Control Point for ERG mode
    try {
      const controlPoint = await service.getCharacteristic(
        BLE_CHARACTERISTICS.fitnessMachineControlPoint
      );
      await controlPoint.startNotifications();
      trainerControlPoint.current = controlPoint;

      // Request control
      await controlPoint.writeValue(ftmsRequestControl() as unknown as BufferSource);
      // Small delay for trainer to process
      await new Promise((r) => setTimeout(r, 200));
      // Start
      await controlPoint.writeValue(ftmsStartOrResume() as unknown as BufferSource);
    } catch {
      // Control point not available - trainer may be read-only
    }

    setTrainerState((prev) => ({
      ...prev,
      connected: true,
      name: device.name || "Smart Trainer",
      ergMode: !!trainerControlPoint.current,
    }));
  }, [handleDisconnect]);

  const disconnectDevice = useCallback(
    (type: DeviceType) => {
      const refs: Record<DeviceType, React.RefObject<DeviceConnection | null>> =
        {
          heartRate: hrConnection,
          power: powerConnection,
          cadence: cadenceConnection,
          trainer: trainerConnection,
        };
      const ref = refs[type];
      if (ref.current?.server.connected) {
        ref.current.server.disconnect();
      }
      handleDisconnect(type)();
    },
    [handleDisconnect]
  );

  const setTargetPower = useCallback(async (watts: number) => {
    if (!trainerControlPoint.current) return;
    try {
      await trainerControlPoint.current.writeValue(
        ftmsSetTargetPower(watts) as unknown as BufferSource
      );
      setTrainerState((prev) => ({ ...prev, targetPower: watts }));
    } catch (e) {
      console.error("Failed to set target power:", e);
    }
  }, []);

  const stopTrainer = useCallback(async () => {
    if (!trainerControlPoint.current) return;
    try {
      await trainerControlPoint.current.writeValue(
        ftmsStop() as unknown as BufferSource
      );
    } catch (e) {
      console.error("Failed to stop trainer:", e);
    }
  }, []);

  const disconnectAll = useCallback(() => {
    (["heartRate", "power", "cadence", "trainer"] as DeviceType[]).forEach(
      disconnectDevice
    );
  }, [disconnectDevice]);

  const state: BluetoothState = {
    isSupported: isBluetoothSupported(),
    heartRate: hrState,
    power: powerState,
    cadence: cadenceState,
    trainer: trainerState,
  };

  const actions: BluetoothActions = {
    connectHeartRate,
    connectPower,
    connectCadence,
    connectTrainer,
    disconnectDevice,
    setTargetPower,
    stopTrainer,
    disconnectAll,
  };

  return [state, actions];
}
