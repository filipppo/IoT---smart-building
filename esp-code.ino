// ----------(c) Electronics-project-hub-------- //
#include "ThingSpeak.h"
#include <ESP8266WiFi.h>
//#include "WiFiManager.h"

#define VIN 3.3  // V power voltage, 3.3v in case of NodeMCU
#define R 10000  // Voltage devider resistor value

//------- WI-FI details ----------//

char ssid[] = "AndroidAP7176";  //SSID here
char pass[] = "lmiw8879";       // Passowrd here
//--------------------------------//

//----------- Channel details ----------------//
unsigned long Channel_ID = 2007557;              // Your Channel ID
unsigned long Channel_ID_read = 2015248;         // Your Channel ID
const char* myWriteAPIKey = "CIWIGMG6WODRK7VY";  //Your write API key
const char* myReadAPIKey = "C7F1EUMD99O64QUR";
//-------------------------------------------//

int x, y;
WiFiClient client;

unsigned long previousMillis = 0;
unsigned long previousMillis_lamp = 0;

// constants won't change :
const long interval = 60000;
const long interval_lamp = 5000;

int PIR = 4;
int LED = 5;

int light_avg = 0;
int move = 0;
int lamp = 0;
int lamp_manual = 0;
int lamp_manual_prev = 0;
int count = 0;
int light_array[60] = { 0 };

//WiFiManager wifiManager;

void setup() {
  Serial.begin(115200);
  pinMode(PIR, INPUT);
  pinMode(LED, OUTPUT);
  WiFi.mode(WIFI_STA);
  ThingSpeak.begin(client);
  internet();
  //wifiManager.autoConnect("ESP-8266");
}

void loop() {
  internet();
  move = checkMove();
  light_array[count++] = checkLight();
  lamp_manual = checkLampManual();
  light_avg = calc_avg();
  unsigned long currentMillis = millis();
  if ((move == 1 && light_avg < 30) || lamp_manual == 1) {
    lamp = 1;
    previousMillis_lamp = currentMillis;    
  } else {
    if (lamp == 1 && ((currentMillis - previousMillis_lamp >= interval_lamp) || lamp_manual_prev != lamp_manual)) {
      lamp = 0;      
    }    
  }

  setLamp(lamp);
  delay(500);

  if ((currentMillis - previousMillis >= interval) || lamp_manual_prev != lamp_manual) {
    previousMillis = currentMillis;
    //Serial.println(light_avg);
    upload();
  }
  lamp_manual_prev = lamp_manual;
}

int calc_avg() {
  int sum = 0;
  for (int i = 0; i < count; i++) {
    sum += light_array[i];
  }
  return (sum / (count + 1));
}

void internet() {
  if (WiFi.status() != WL_CONNECTED) {
    while (WiFi.status() != WL_CONNECTED) {
      WiFi.begin(ssid, pass);
      delay(5000);
      Serial.print("Próba");
    }
    Serial.print("Połączono");
  }
}

int checkMove() {
  int move = digitalRead(PIR);  //odczytanie wartości z czujnika
  if (move == HIGH)             //wyświetlenie informacji na monitorze szeregowym
  {                             //stan wysoki oznacza wykrycie ruchu, stan niski - brak ruchu
    //Serial.println("RUCH WYKRYTY!");
  } else {
    //Serial.println("brak ruchu");
  }
  return move;
}

int checkLight() {
  float Vout = analogRead(A0) * (VIN / float(1023));
  float RLDR = (R * (VIN - Vout)) / Vout;
  int lux = 500 / (RLDR / 1000);
  Serial.println(lux);
  return lux;
}

int checkLampManual() {
  int lamp_man = ThingSpeak.readIntField(Channel_ID_read, 1);
  //int statusCode = ThingSpeak.getLastReadStatus();
  //Serial.println(lamp_man);
  //Serial.print("Status");
  //Serial.println(statusCode);
  return lamp_man;
}

void setLamp(int state) {
  if (state == 1) {
    digitalWrite(LED, HIGH);
  } else {
    digitalWrite(LED, LOW);
  }
}

void upload() {
  // set the fields with the values
  ThingSpeak.setField(1, light_avg);
  ThingSpeak.setField(2, move);
  ThingSpeak.setField(3, lamp);
  // write to the ThingSpeak channel
  int x = ThingSpeak.writeFields(Channel_ID, myWriteAPIKey);
  if (x == 200) {
    Serial.println("Channel update successful.");
  } else {
    Serial.println("Problem updating channel. HTTP error code " + String(x));
  }
  count = 0;
}