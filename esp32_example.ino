/*
 * ESP32 Sensor Data Sender
 *
 * This example sends sensor data to your FastAPI backend
 *
 * Required Libraries:
 * - WiFi (built-in)
 * - HTTPClient (built-in)
 * - ArduinoJson (install via Library Manager)
 *
 * Adjust the sensor reading functions based on your actual hardware
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============ CONFIGURATION ============
// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// API configuration
const char* serverUrl = "https://your-app.vercel.app/api/data";
const char* apiKey = "your-api-key";
const char* deviceId = "ESP32_001";

// Sensor configuration
#define SEND_INTERVAL 60000  // Send data every 60 seconds
#define DHT_PIN 4            // Example: DHT sensor on GPIO 4

// ============ GLOBAL VARIABLES ============
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n=== ESP32 Data Sender ===");

  // Initialize sensors here
  // Example: dht.begin();

  // Connect to WiFi
  connectToWiFi();
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Reconnecting...");
    connectToWiFi();
  }

  // Send data at specified interval
  if (millis() - lastSendTime >= SEND_INTERVAL) {
    sendSensorData();
    lastSendTime = millis();
  }

  delay(100);
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\nFailed to connect to WiFi");
  }
}

void sendSensorData() {
  Serial.println("\n--- Reading Sensors ---");

  // Read sensor values
  float temperature = readTemperature();
  float humidity = readHumidity();
  float pressure = readPressure();

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  // Send to API
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    Serial.println("\n--- Sending Data to API ---");
    http.begin(serverUrl);

    // Set headers
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", apiKey);

    // Create JSON payload
    StaticJsonDocument<512> doc;
    doc["device_id"] = deviceId;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["pressure"] = pressure;

    // Additional data object
    JsonObject additionalData = doc.createNestedObject("additional_data");
    additionalData["battery"] = getBatteryLevel();
    additionalData["signal_strength"] = WiFi.RSSI();
    additionalData["free_heap"] = ESP.getFreeHeap();
    additionalData["uptime"] = millis() / 1000;

    // Serialize to string
    String jsonPayload;
    serializeJson(doc, jsonPayload);

    Serial.print("Payload: ");
    Serial.println(jsonPayload);

    // Send POST request
    int httpResponseCode = http.POST(jsonPayload);

    // Handle response
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      String response = http.getString();
      Serial.print("Response: ");
      Serial.println(response);

      if (httpResponseCode == 201) {
        Serial.println("✓ Data sent successfully!");
      }
    } else {
      Serial.print("✗ Error sending data. Error code: ");
      Serial.println(httpResponseCode);

      // Common error codes
      if (httpResponseCode == -1) {
        Serial.println("  Connection failed");
      } else if (httpResponseCode == -11) {
        Serial.println("  Timeout");
      }
    }

    http.end();
  } else {
    Serial.println("✗ WiFi not connected. Skipping data send.");
  }
}

// ============ SENSOR READING FUNCTIONS ============
// Implement these based on your actual sensors

float readTemperature() {
  // Example implementation for DHT sensor:
  // return dht.readTemperature();

  // For testing, return random value:
  return random(200, 300) / 10.0;  // 20.0 - 30.0 °C
}

float readHumidity() {
  // Example implementation for DHT sensor:
  // return dht.readHumidity();

  // For testing, return random value:
  return random(400, 800) / 10.0;  // 40.0 - 80.0 %
}

float readPressure() {
  // Example implementation for BMP/BME sensor:
  // return bmp.readPressure() / 100.0;

  // For testing, return random value:
  return random(9800, 10300) / 10.0;  // 980.0 - 1030.0 hPa
}

int getBatteryLevel() {
  // If you have a battery with voltage divider on ADC pin:
  // int analogValue = analogRead(BATTERY_PIN);
  // float voltage = analogValue * (3.3 / 4095.0) * 2;  // Adjust based on divider
  // return map(voltage * 100, 320, 420, 0, 100);  // 3.2V-4.2V for LiPo

  // For testing:
  return 100;
}

/*
 * ============ SENSOR SETUP EXAMPLES ============
 *
 * For DHT22 Temperature/Humidity Sensor:
 * ------------------------------------------
 * #include <DHT.h>
 * #define DHT_PIN 4
 * #define DHT_TYPE DHT22
 * DHT dht(DHT_PIN, DHT_TYPE);
 *
 * In setup():
 * dht.begin();
 *
 *
 * For BMP280/BME280 Pressure Sensor:
 * ------------------------------------------
 * #include <Adafruit_BMP280.h>
 * Adafruit_BMP280 bmp;
 *
 * In setup():
 * if (!bmp.begin(0x76)) {
 *   Serial.println("BMP280 not found!");
 * }
 *
 *
 * For Analog Sensors:
 * ------------------------------------------
 * #define ANALOG_PIN 34
 *
 * int value = analogRead(ANALOG_PIN);
 * float voltage = value * (3.3 / 4095.0);
 */
