// MPU-6050 Short Example Sketch
// By Arduino User JohnChi
// August 17, 2014
// Public Domain
#include<Wire.h>
#define FB_REGISTER_ADDR_LEDS_TOP					0x00
//#define TWI_MASTER_CONFIG_CLOCK_PIN_NUMBER (24U)
//#define TWI_MASTER_CONFIG_DATA_PIN_NUMBER (25U)
//#define MPU6050_I2C_ADDRESS (25U)
#define MPU_addr                                                         0x01

int debug_id = 0;
int startOfLine = 1;
String sent = "";

//const int MPU_addr = FB_REGISTER_ADDR_LEDS_TOP;  // this should be the address of the Faceboard itself
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
void setup(){
  char bytes[] = "abc";
  int numBytes = 3;
  char var;
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x33);  // IR leds,
  Wire.write(0x0F);  // turn all leds on
  //Wire.write(0x00);
  //Wire.write(0x00);
  //memcpy(&var, bytes, numBytes);
  //Wire.write(var);
  //Serial.print("red led o2");
  Wire.endTransmission(true);
  Serial.begin(9600);
  Serial.write('1');
}

void loop(){
  debug_id++;
  //  Wire.beginTransmission(MPU_addr);
  //  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  //  Wire.endTransmission(false);
  //  Wire.requestFrom(MPU_addr,14,true);  // request a total of 14 registers
  //  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)     
  //  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  //  AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  //  Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  //  GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  //  GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  //  GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
  //  Serial.print("AcX = "); Serial.print(AcX);
  //  Serial.print(" | AcY = "); Serial.print(AcY);
  //  Serial.print(" | AcZ = "); Serial.print(AcZ);
  //  Serial.print(" | Tmp = "); Serial.print(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
  //  Serial.print(" | GyX = "); Serial.print(GyX);
  //  Serial.print(" | GyY = "); Serial.print(GyY);
  //  Serial.print(" | GyZ = "); Serial.println(GyZ);
  //  Serial.println("in a loop");
  //  delay(1000);
  //Wire.beginTransmission(MPU_addr);
  //Wire.write(0x20);  // IR leds,
  //Wire.write(0x00);  // turn all leds on
  //Wire.endTransmission(true);
  //delay(100);
  //char bytes[] = "fbrgbled rb tb 1 2 3 4";
  int numBytes = 5;
  uint8_t num;
 
  if(Serial.available()>0){
    //Serial.println(Serial.available());
//    Wire.beginTransmission(MPU_addr);
//    Wire.write(0x00);
//    Wire.write(0x01);
//    delay(1000);
//    Wire.endTransmission(true);
//    Wire.beginTransmission(MPU_addr);
//    Wire.write(0x00);
//    Wire.write(0x00);
//    delay(1000);
//    Wire.endTransmission(true);
    
    Wire.beginTransmission(MPU_addr);
    Wire.write(0x30);  // IR leds,
    if (startOfLine == 1){
    //Wire.write(0xB7);  // turn all leds on
    //Wire.write(0xB7);
    //Wire.write(0xB7);
  }


    startOfLine = 2;

    
//    String str;
//    str = Serial.readString();
//    int length;
//    length = str.length();
//    Wire.write((((uint16_t) length / 1000) % 10)-'0');
//    Wire.write((((uint16_t) length /  100) % 10)-'0');
//    Wire.write((((uint16_t) length /   10) % 10)-'0');
//    Wire.write((((uint16_t) length /    1) % 10)-'0');
////    Wire.write('a');
//    for (int i=1;i<length;i++){
////      Wire.write('b');
//      char byte = Serial.read();
//      Wire.write(byte);
//      Wire.write('c');
//    }
    //Wire.write('d');
    //while (startOfLine != 1){
      char data[100];
      int length;
      length = Serial.readBytesUntil('\n', data, 2);
      if(length != 2){
        startOfLine = 1;}
  //    //char length = Serial.read();
  //    //int i = length - '0';
      //Wire.write(0x7C);  // turn all leds on
      //Wire.write(0x7C);
      //Wire.write(0x7C);
      for (int i = 0; i < length; ++i) {
         Wire.write(data[i]); 
         String temp = String(data[i]);
         //Serial.write(data[i]);
         sent = String(sent + temp);
      }
    //}
    Serial.write('0');
    Serial.print(sent);
    Wire.endTransmission(true);
  //Serial.println(num);
//    Wire.write(0x00);
//    if (Serial.read() == '1'){
//    Wire.write(0x04);}
//    else {
//      Wire.write(0x01);}
  //  Wire.write(0x00);
  //  Wire.write(0x07);
    //Serial.println("starting delay");
    //delay(100);
//    Wire.beginTransmission(MPU_addr);
//    Wire.write(0x00);
//    Wire.write(0x00);
//    Wire.endTransmission(true);
//    delay(1000);
    Serial.flush();
  }
}
//  
//  
//  // Read the raw values.
//  // Read 14 bytes at once, 
//  // containing acceleration, temperature and gyro.
//  // With the default settings of the MPU-6050,
//  // there is no filter enabled, and the values
//  // are not very stable.
//  error = MPU6050_read (MPU6050_ACCEL_XOUT_H, (uint8_t *) &accel_t_gyro, sizeof(accel_t_gyro));
//  Serial.print(F("Read accel, temp and gyro, error = "));
//  Serial.println(error,DEC);
//}
//
//// --------------------------------------------------------
//// MPU6050_read
////
//// This is a common function to read multiple bytes 
//// from an I2C device.
////
//// It uses the boolean parameter for Wire.endTransMission()
//// to be able to hold or release the I2C-bus. 
//// This is implemented in Arduino 1.0.1.
////
//// Only this function is used to read. 
//// There is no function for a single byte.
////
//int MPU6050_read(int start, uint8_t *buffer, int size)
//{
//  int i, n, error;
//
//  Wire.beginTransmission(MPU6050_I2C_ADDRESS);
//  n = Wire.write(start);
//  if (n != 1)
//    return (-10);
//
//  n = Wire.endTransmission(false);    // hold the I2C-bus
//  if (n != 0)
//    return (n);
//
//  // Third parameter is true: relase I2C-bus after data is read.
//  Wire.requestFrom(MPU6050_I2C_ADDRESS, size, true);
//  i = 0;
//  while(Wire.available() && i<size)
//  {
//    buffer[i++]=Wire.read();
//  }
//  if ( i != size)
//    return (-11);
//
//  return (0);  // return : no error
//}

