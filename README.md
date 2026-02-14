# ESP32 Data Collection API

A FastAPI backend designed to receive and store data from ESP32 edge devices, deployable on Vercel.

## Features

- ✅ FastAPI with automatic API documentation
- ✅ PostgreSQL database support (Vercel Postgres compatible)
- ✅ SQLite support for local development
- ✅ API key authentication
- ✅ Flexible sensor data schema
- ✅ REST API endpoints for data retrieval
- ✅ Ready for Vercel serverless deployment

## Project Structure

```
Server/
├── api/
│   ├── __init__.py
│   ├── index.py          # Main FastAPI application
│   ├── database.py       # Database configuration
│   ├── models.py         # SQLAlchemy models
│   └── schemas.py        # Pydantic schemas
├── main.py               # Local development server
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel deployment config
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Local Development Setup

### 1. Clone and Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your variables
# For local development, SQLite is used by default
```

### 3. Run Local Server

```bash
# Using uvicorn directly
uvicorn main:app --reload

# Or using Python
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Vercel Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Set Up Vercel Postgres (Recommended)

1. Go to your Vercel dashboard
2. Create a new Postgres database
3. Copy the connection string

### 3. Configure Environment Variables

In your Vercel project settings, add:

```
DATABASE_URL = your-postgres-connection-string
API_KEY = your-secure-api-key
```

### 4. Deploy

```bash
vercel
```

## API Endpoints

### Health Check
```
GET /
GET /health
```

### Send Data from ESP32
```
POST /api/data
Headers: X-API-Key: your-api-key
Body: {
  "device_id": "ESP32_001",
  "temperature": 25.5,
  "humidity": 60.0,
  "pressure": 1013.25,
  "additional_data": {"battery": 85}
}
```

### Retrieve Data
```
GET /api/data?skip=0&limit=100&device_id=ESP32_001
Headers: X-API-Key: your-api-key
```

### Get Specific Data Entry
```
GET /api/data/{id}
Headers: X-API-Key: your-api-key
```

### List All Devices
```
GET /api/devices
Headers: X-API-Key: your-api-key
```

## ESP32 Arduino Code Example

### Install Required Libraries

In Arduino IDE, install:
- WiFi (built-in)
- HTTPClient (built-in)
- ArduinoJson (by Benoit Blanchon)

### Example Code

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// API configuration
const char* serverUrl = "https://your-app.vercel.app/api/data";
const char* apiKey = "your-api-key";
const char* deviceId = "ESP32_001";

// Sensor pins (adjust based on your setup)
// Example: DHT22 sensor for temperature/humidity
#define SENSOR_PIN 4

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // Read sensor data
    float temperature = readTemperature();  // Implement based on your sensor
    float humidity = readHumidity();        // Implement based on your sensor
    float pressure = readPressure();        // Implement based on your sensor

    // Send data to API
    sendDataToAPI(temperature, humidity, pressure);
  } else {
    Serial.println("WiFi Disconnected");
  }

  // Wait 60 seconds before next reading
  delay(60000);
}

void sendDataToAPI(float temp, float hum, float press) {
  HTTPClient http;

  // Begin HTTP connection
  http.begin(serverUrl);

  // Set headers
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", apiKey);

  // Create JSON payload
  StaticJsonDocument<256> doc;
  doc["device_id"] = deviceId;
  doc["temperature"] = temp;
  doc["humidity"] = hum;
  doc["pressure"] = press;

  // Add additional data
  JsonObject additionalData = doc.createNestedObject("additional_data");
  additionalData["battery"] = getBatteryLevel();  // Implement if needed
  additionalData["signal_strength"] = WiFi.RSSI();

  // Serialize JSON
  String jsonPayload;
  serializeJson(doc, jsonPayload);

  // Send POST request
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    Serial.print("Response: ");
    Serial.println(response);
  } else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
    Serial.println("Error sending data");
  }

  http.end();
}

// Implement these functions based on your actual sensors
float readTemperature() {
  // Example: return random value for testing
  return random(200, 300) / 10.0;
}

float readHumidity() {
  return random(400, 800) / 10.0;
}

float readPressure() {
  return random(9800, 10300) / 10.0;
}

int getBatteryLevel() {
  // Implement battery reading if applicable
  return 100;
}
```

## Database Schema

The `sensor_data` table includes:

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary key |
| device_id | String | ESP32 device identifier |
| timestamp | DateTime | Auto-generated timestamp |
| temperature | Float | Temperature in Celsius (optional) |
| humidity | Float | Humidity percentage (optional) |
| pressure | Float | Pressure in hPa (optional) |
| additional_data | JSON | Flexible field for extra data (optional) |

## Security Considerations

1. **API Key**: Always use a strong API key and keep it secret
2. **HTTPS**: Vercel provides HTTPS by default
3. **CORS**: Configure allowed origins in production
4. **Rate Limiting**: Consider adding rate limiting for production
5. **Database**: Use Vercel Postgres or secure database service

## Troubleshooting

### ESP32 Connection Issues
- Check WiFi credentials
- Verify API URL is correct (https://)
- Ensure API key matches server configuration
- Check Serial Monitor for error messages

### Database Issues
- Verify DATABASE_URL environment variable
- For Vercel, ensure Postgres database is created and linked
- Check database connection logs in Vercel dashboard

### API Issues
- Check API documentation at `/docs` endpoint
- Verify request format matches schema
- Check API key is included in headers

## License

MIT License
