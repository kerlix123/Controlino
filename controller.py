from finder import find_arduino

arduino = None
port_name = None

def get_arduino():
    global arduino, port_name
    finder = find_arduino()
    if finder:
        arduino = finder["serial"]
        port_name = finder["name"]
        return True
    else:
        return False
    

def send_cmd(cmd):
    if arduino:
        arduino.write((cmd + "\n").encode())


def send_instruction(pin, pin_mode, ad_mode, value):
    pin_mode_value = "INPUT" if pin_mode == "Read" else "OUTPUT"
    ad_mode_value = "DIGITAL" if ad_mode == "Digital" else "ANALOG"
    send_cmd(f"PIN_{pin}_{pin_mode_value}_{ad_mode_value}_{value}")

    response = arduino.readline().decode(errors="ignore").strip().split("_")
    return response