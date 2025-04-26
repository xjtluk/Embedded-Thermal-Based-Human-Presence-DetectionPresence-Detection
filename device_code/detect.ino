#include <Wire.h>
#include <Adafruit_MLX90640.h>
#include <test_inferencing.h>             // Edge Impulse exported library

// Device and model parameters
Adafruit_MLX90640 mlx;
const uint16_t kNumPixels = 32 * 24;      // 768
const int LED_PIN = LED_BUILTIN;
const int BUZZER_PIN = 11;                // Buzzer connected to D3 pin

// Voting window settings
const int HISTORY_SIZE = 4;               // 1 second ≈ 4 frames @4 Hz
bool history[HISTORY_SIZE] = {0};
int histPos = 0;

// Timed output
unsigned long lastReport = 0;
const unsigned long REPORT_INTERVAL = 1000;  // 1 second

// Frame data buffer
float frameBuf[kNumPixels];

void setup() {
  Serial.begin(115200);
  while (!Serial);

  // Initialize MLX90640
  Wire.begin();
  Wire.setClock(400000);
  if (!mlx.begin(0x33, &Wire)) {
    Serial.println("MLX90640 initialization failed!");
    while (1) delay(10);
  }
  mlx.setMode(MLX90640_CHESS);
  mlx.setResolution(MLX90640_ADC_18BIT);
  mlx.setRefreshRate(MLX90640_4_HZ);       // 4 Hz refresh rate

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);            // Initialize buzzer pin
  digitalWrite(LED_PIN, LOW);

  lastReport = millis();
}

void loop() {
  // 1. Read a thermal frame
  if (mlx.getFrame(frameBuf) != 0) {
    delay(250);
    return;
  }

  // 2. Construct Time Series signal
  signal_t signal;
  signal.total_length = kNumPixels;
  signal.get_data = [&](size_t offset, size_t length, float *out_ptr) {
    memcpy(out_ptr, frameBuf + offset, length * sizeof(float));
    return EI_IMPULSE_OK;
  };

  // 3. Single-frame inference
  ei_impulse_result_t result;
  if (run_classifier(&signal, &result, false) != EI_IMPULSE_OK) {
    Serial.println("Inference error");
    delay(250);
    return;
  }

  // 4. Store single-frame decision
  bool personNow = (result.classification[0].value
                    > result.classification[1].value); // “person” vs “empty”
  history[histPos++] = personNow;
  if (histPos >= HISTORY_SIZE) histPos = 0;

  // 5. Output final voting result every second
  unsigned long now = millis();
  if (now - lastReport >= REPORT_INTERVAL) {
    lastReport = now;
    int votes = 0;
    for (int i = 0; i < HISTORY_SIZE; i++) votes += history[i];
    bool finalPerson = (votes > (HISTORY_SIZE/2));

    // Serial output
    Serial.print("Final (1s): ");
    Serial.println(finalPerson ? "PERSON" : "EMPTY");

    // LED indication
    digitalWrite(LED_PIN, finalPerson ? HIGH : LOW);

    // Buzzer control (4kHz frequency)
    if (finalPerson) {
      tone(BUZZER_PIN, 4000);  // Buzzer sounds when a person is detected
    } else {
      noTone(BUZZER_PIN);      // Silent when no one is detected
    }
  }

  delay(1);  // Slight delay to keep the loop smooth
}