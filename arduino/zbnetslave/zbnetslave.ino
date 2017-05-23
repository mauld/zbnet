#include <DHT.h>
#include <Printers.h>
#include <XBee.h>
#include "binary.h"
const int MAX_DIGITAL_PINS = 12;
XBeeWithCallbacks xbee;
#define XBeeSerial Serial
int digitalState[MAX_DIGITAL_PINS];
int digitalMode[MAX_DIGITAL_PINS];

// =============================================================== //
// Setup Loop                                                      //
// =============================================================== //
void setup() {
  // initialize

  for (int x=0; x<MAX_DIGITAL_PINS; x++){
    digitalState[x] = 0;
  }

  
  XBeeSerial.begin(9600);
  delay(1);
  xbee.onZBRxResponse(processRxPacket);
  
}

// =============================================================== //
// Main Loop                                                       //
// =============================================================== //
void loop() {
  xbee.loop();

  //check all the digital sensors and send packet if there has been an update
  for (int x=0;x<MAX_DIGITAL_PINS; x++){
    if (digitalMode[x] == 1){
      digital_read_passive(x);
    }
  }
 

 
  

}


//SENDS PACKET TO COORDINATOR
void sendData(AllocBuffer<100> &packet){
  ZBTxRequest txRequest;
  txRequest.setAddress64(0x0000000000000000);
  txRequest.setPayload(packet.head,packet.len());
  xbee.send(txRequest);
}

//set pin mode
void set_pin_mode(uint8_t pin, uint16_t value){
  if (value == 0x01){
     pinMode(pin, INPUT);
     digitalMode[pin] = 1;
  } else if (value == 0x02){
    pinMode(pin, OUTPUT);
    digitalMode[pin] = 0;
  } else if (value == 0x03){
    digitalMode[pin] = 0;
    pinMode(pin, INPUT);
  } else if (value == 0x04){
    digitalMode[pin] = 0;
    pinMode(pin, OUTPUT);
  }

  uint8_t command = 0x01;
  AllocBuffer<100> packet;
  packet.append<uint8_t>(command);
  packet.append<uint8_t>(pin);
  packet.append<uint16_t>(value);
  sendData(packet);
}

//digital write
void digital_write(uint8_t pin, uint16_t value){
  if (value == 0x01){
    digitalWrite(pin, HIGH);
  } else {
    digitalWrite(pin, LOW);
  }
  uint8_t command = 0x02;
  AllocBuffer<100> packet;
  packet.append<uint8_t>(command);
  packet.append<uint8_t>(pin);
  packet.append<uint16_t>(value);
  sendData(packet);
  
}

//analog read
void analog_read(uint8_t pin){
  
  uint16_t value;
  value = analogRead(pin);
  
  uint8_t command = 0x04;
  AllocBuffer<100> packet;
  packet.append<uint8_t>(command);
  packet.append<uint8_t>(pin);
  packet.append<uint16_t>(value);
  sendData(packet);
}

//digital read
void digital_read(uint8_t pin){
  int var;
  uint16_t value;
  var = digitalRead(pin);
  if (var == HIGH){
    value = 0x01;
  } else if(var == LOW) {
    value = 0x00;
  };
  uint8_t command = 0x03;
  AllocBuffer<100> packet;
  packet.append<uint8_t>(command);
  packet.append<uint8_t>(pin);
  packet.append<uint16_t>(value);
  sendData(packet);
  
  
  
  
}

void digital_read_passive(uint8_t pin){
  int var;
  uint16_t value;
  var = digitalRead(pin);
  if (var == HIGH){
    value = 0x01;
  } else if(var == LOW) {
    value = 0x00;
  };
  if (var != digitalState[pin]){
    uint8_t command = 0x03;
    AllocBuffer<100> packet;
    packet.append<uint8_t>(command);
    packet.append<uint8_t>(pin);
    packet.append<uint16_t>(value);
    sendData(packet);
    digitalState[pin]=var;
  }
  
  
}
// =============================================================== //
// Main Receiver                                                   //
// =============================================================== //
void processRxPacket(ZBRxResponse& rx, uintptr_t){

  Buffer b(rx.getData(),rx.getDataLength());
  Buffer original = b;
  uint8_t command = b.remove<uint8_t>();
  uint8_t pin = b.remove<uint8_t>();
  uint16_t value;
  if (b.len() > 0 ){
    value = b.remove<uint16_t>();
  }

  if (command == 0x01){
    set_pin_mode(pin, value);
  } else if (command == 0x02){
    digital_write(pin, value);
  } else if (command == 0x03) {
    digital_read(pin);
  } else if (command == 0x04){
    analog_read(pin);
  }
  
};


