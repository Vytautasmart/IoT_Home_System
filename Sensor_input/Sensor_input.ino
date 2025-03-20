#include "DHT.h"

#define DHTPIN 7         // DHT22 connected to digital pin 7
#define DHTTYPE DHT22

#define LDR_PIN A0
#define TRIG_PIN 9
#define ECHO_PIN 10

DHT dht(DHTPIN, DHTTYPE);

int lightThreshold = 300;
int distanceThreshold = 100;

void setup() {
  Serial.begin(115200);
  pinMode(LDR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  dht.begin();
}

void loop() {
  // Read LDR value
  int light = analogRead(LDR_PIN);
  
  // Read distance from HC-SR04
  long duration, distance;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration * 0.034) / 2;

  // Read temperature from DHT22
  float temperature = dht.readTemperature();

  // Send data over Serial
  Serial.print(light);
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.println(temperature);

  delay(500);
}
