#include <Wire.h>
#include <Adafruit_MLX90640.h>

Adafruit_MLX90640 mlx;
const int numPixels = 768;  // 32x24

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10); // Wait for serial connection
  
  Serial.println("Initializing I2C bus...");
  Wire.begin();
  Wire.setClock(400000);  // Set I2C clock frequency to 400kHz

  Serial.println("Initializing MLX90640 sensor...");
  if (!mlx.begin(0x33, &Wire)) {
    Serial.println("MLX90640 initialization failed!");
    while (1) delay(10);
  }
  Serial.println("MLX90640 initialization successful!");

  // Configure sensor parameters
  mlx.setMode(MLX90640_CHESS);
  mlx.setResolution(MLX90640_ADC_19BIT);
  mlx.setRefreshRate(MLX90640_4_HZ);  // Lower frame rate to reduce I2C load
}

void loop() {
  float frame[numPixels];
  int status = mlx.getFrame(frame);
  if (status != 0) {
    Serial.print("Failed to get frame data, error code: ");
    Serial.println(status);
    delay(500);
    return;
  }
  
  // Output frame marker
  Serial.println("START_FRAME");

  // Output data, 32 values per line
  for (int i = 0; i < numPixels; i++) {
    Serial.print(frame[i], 2);
    if ((i + 1) % 32 == 0)
      Serial.println();
    else
      Serial.print(",");
  }
  
  Serial.println("END_FRAME");
  Serial.println();  // Output an extra blank line for separation

  delay(250);
}
