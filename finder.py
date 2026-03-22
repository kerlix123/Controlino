import serial
import serial.tools.list_ports
import time


def find_arduino():
    ports = serial.tools.list_ports.comports()

    for port in ports:
        print("Checking:", port.device)

        try:
            ser = serial.Serial(port.device, 115200, timeout=2)
            time.sleep(3)

            ser.reset_input_buffer()

            ser.write(b"PING\n")
            ser.flush()

            time.sleep(0.2)

            response = ser.readline().decode(errors="ignore").strip()
            print("Response:", repr(response))

            if "ARDUINO_OK" in response:
                print("Arduino on", port.device)
                return {"serial": ser, "name": port.device}

            ser.close()

        except Exception as e:
            print("Error on", port.device, ":", e)

    return None
