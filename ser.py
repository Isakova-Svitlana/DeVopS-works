#!/usr/bin/python

import time
import serial

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 1
ser.xonxoff = False
ser.rtscts = False
ser.dsrdtr = False
ser.writeTimeout = 2


def loadData(ser):
    buffer = ser.read(1)
    if (buffer != ''):
        try:
            print buffer
        except Exception, e:
            print str(e)
            pass


try:
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()
if ser.isOpen():

    input = 1
    try:
        ser.flushInput()
        ser.flushOutput()
        ser.write("\r\n\r\n")
        time.sleep(1)
        input_data = ser.read(ser.inWaiting())
        if 'Username' in input_data:
            ser.write('mgv' + '\r\n')
            time.sleep(1)
        input_data = ser.read(ser.inWaiting())
        if 'Password' in input_data:
            ser.write('pcYb7Ynt' + '\r\n')
            time.sleep(1)
        if '>' in input_data:
            ser.write('enable' + '\r\n')
            time.sleep(1)
        input_data = ser.read(ser.inWaiting())
        print input_data

        while True:
            # input = raw_input(">> ")
            input = "ret\r\n"
            input += "system-view\r\n"
            input += "interface ethe 0/0/14\r\n"
            input += "port hybrid tagged vlan 28\r\n"
            input += "ret\r\n"
            # input += "display vlan 28\r\n"
            # input += "tftp 172.18.8.2 get huawei.cfg"
            if input == 'exit':
                ser.close()
                exit()
            else:
                ser.write(input)
                # print(input)
                out = ''
                time.sleep(1)

                numOfLines = 0

                while ser.inWaiting() > 0:
                    # s = loadData(ser)
                    # # out = ser.readline()
                    out += ser.read(1)
                    # if response == " ---- More ----":
                    # ser.write('\r\n')
                    # print(out)
                    # numOfLines = numOfLines + 1
                    # if (numOfLines >= 5):
                    #    break
                print(out)
                ser.close()
    except Exception, e1:
        print "error communicating...: " + str(e1)
else:
    print "cannot open serial port "
