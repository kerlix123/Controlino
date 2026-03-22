void setup() {
  Serial.begin(115200);
  //pinMode(A3, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg == "PING") {
      Serial.println("ARDUINO_OK");
    } else if (msg.substring(0, 4) == "PIN_") {
      int last = 4, index = 0, pin = -1;
      bool input = true;
      bool analog = true;

      for (uint8_t i = 4; i < msg.length(); i++) {
        if (msg[i] == '_') {
          String s = msg.substring(last, i);
          if (index == 0) {
            // pin
            pin = s.toInt();
          } else if (index == 1) {
            // pin mode
            if (s == "OUTPUT")
              input = false;
          } else if (index == 2) {
            if (s == "DIGITAL")
              analog = false;
          }
          last = i + 1;
          index++;
        }
      }

      int value = msg.substring(last).toInt();
      if (input) {
        pinMode(pin, INPUT);
        Serial.print("VALUE_");
        if (analog) {
          Serial.println(analogRead(pin));
        } else {
          Serial.println(digitalRead(pin));
        }
      } else {
        pinMode(pin, OUTPUT);
        if (analog) {
          analogWrite(pin, value);
        } else {
          Serial.println("lele");
          digitalWrite(pin, value);
        }
      }
    }
  }
}