#include <Wire.h>
#include <Adafruit_MLX90640.h>

Adafruit_MLX90640 mlx;
const int numPixels = 768;  // 32x24

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10); // 等待串口连接
  
  Serial.println("初始化I2C总线...");
  Wire.begin();
  Wire.setClock(400000);  // 设置I2C时钟频率为400kHz

  Serial.println("初始化MLX90640传感器...");
  if (!mlx.begin(0x33, &Wire)) {
    Serial.println("MLX90640 初始化失败！");
    while (1) delay(10);
  }
  Serial.println("MLX90640 初始化成功！");

  // 配置传感器参数
  mlx.setMode(MLX90640_CHESS);
  mlx.setResolution(MLX90640_ADC_19BIT);
  mlx.setRefreshRate(MLX90640_4_HZ);  // 降低帧率，减少I2C负载
}

void loop() {
  float frame[numPixels];
  int status = mlx.getFrame(frame);
  if (status != 0) {
    Serial.print("获取帧数据失败，错误码：");
    Serial.println(status);
    delay(500);
    return;
  }
  
  // 输出帧标记
  Serial.println("START_FRAME");

  // 输出数据，每32个数据为一行
  for (int i = 0; i < numPixels; i++) {
    Serial.print(frame[i], 2);
    if ((i + 1) % 32 == 0)
      Serial.println();
    else
      Serial.print(",");
  }
  
  Serial.println("END_FRAME");
  Serial.println();  // 多输出一行空行分隔

  delay(250);
}
