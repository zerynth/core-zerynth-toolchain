
#refer to vhal_pins.h

vipernames = {}

classes = {
    "D":0x0000,
    "A":0x0100,
    "SPI":0x0200,
    "I2C":0x0300,
    "PWM":0x0400,
    "ICU":0x0500,
    "CAN":0x0600,
    "SER":0x0700,
    "DAC":0x0800,
    "LED":0x0900,
    "BTN":0x0A00
}

vcls = {
    "SPI":["MOSI","MISO","SCLK"],
    "I2C":["SDA","SCL"],
    "SER":["RX","TX"],
    "CAN":["CANRX","CANTX"]
}

#define PRPH_EXT    0x00
#define PRPH_ADC    0x01
#define PRPH_SPI    0x02
#define PRPH_I2C    0x03
#define PRPH_PWM    0x04
#define PRPH_ICU    0x05
#define PRPH_CAN    0x06
#define PRPH_SER    0x07
#define PRPH_DAC    0x08
#define PRPH_MAC    0x09
#define PRPH_SDC    0x0A
#define PRPH_USB    0x0B


prphs = {
    "SERIAL":0x700,
    "SPI":0x0200,
    "I2C":0x0300,
    "ADC":0x0100,
    "PWMD":0x0400,
    "ICUD":0x0500,
    "CAN":0x0600,
}

for k,v in classes.items():
    if k in vcls:
        lst =vcls[k]
        for x in range(0,128):
            vipernames[lst[x%len(lst)]+str(x//len(lst))]=classes[k]+x
    else:
        for x in range(0,128):
            vipernames[k+str(x)]=classes[k]+x

for k,v in prphs.items():
    for x in range(0,32):
        vipernames[k+str(x)]=v+x


viperpinmap ={
}


fnx = ["PWM","ICU","DAC","MOSI","MISO","SCLK","SDA","SCL","CANRX","CANTX","RX","TX"]
for x in range(0,128):
    viperpinmap["D"+str(x)]={k:k+str(x) for k in fnx}
    viperpinmap["D"+str(x)]["ADC"]="A"+str(x)
    viperpinmap["A"+str(x)]=viperpinmap["D"+str(x)]

