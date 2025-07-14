import smbus
from time import sleep, time
import RPi.GPIO as GPIO  # Raspberry Pi GPIO library
import sys
import serial
import json
import geopy.distance

# GPIO pins and constants
no_help_but = 12
red_led = 11
green_led = 13
timer = 15.0
AT_FLAG = True
noti_flag = True
buttonState = 0
acci_time = 0.0
power_key = 4

# MPU6050 Registers
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47
TEMP_OUT0 = 0x41

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(no_help_but, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(red_led, GPIO.OUT)
GPIO.setup(green_led, GPIO.OUT)

# Initialize serial for SIM7000X
ser = serial.Serial('/dev/ttyS0', baudrate=115200)
ser.flushInput()

# I2C bus and device address
bus = smbus.SMBus(1)
Device_Address = 0x68  # MPU6050 device address

# Global variables
flag = True
rec_buff = ''
rec_buff2 = ''
time_count = 0
msg = ''
hos_name = ""
hos_num = 0
em_pho_no = 7977875992

def MPU_Init():
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
    bus.write_byte_data(Device_Address, CONFIG, 0)
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)
    value = (high << 8) | low
    if value > 32768:
        value = value - 65536
    return value

MPU_Init()

print("Reading Data of Gyroscope and Accelerometer")
print("Reading the latest DATABASE .....")

with open("/home/pi/hub_coords.json", mode='r') as read_file:
    data = json.load(read_file)
    data = list(data)

with open("/home/pi/police_coords.json", mode='r') as read_file:
    data_police = json.load(read_file)
    data_police = list(data_police)

def main_sms(msg1, num):
    print("HERE 1")
    ser.write(b"AT+CMGF=1\r")
    print("HERE 2")
    sleep(1)
    ser.write(f'AT+CMGS="{num}"\r'.encode())
    print("sending message")
    sleep(2)
    ser.reset_output_buffer()
    sleep(1)
    ser.write(str.encode(msg1 + chr(26)))  # Ctrl+Z to send
    sleep(3)
    print("message sent")

def send_at(command, back, timeout):
    global msg, AT_FLAG, noti_flag, rec_buff

    ser.write((command + '\r\n').encode())
    sleep(timeout)

    rec_buff = ''
    if ser.inWaiting():
        rec_buff = ser.read(ser.inWaiting())

    if rec_buff != b'':
        if back not in rec_buff.decode():
            print(command + ' ERROR')
            print(command + ' back:\t' + rec_buff.decode())
            return 0
        else:
            print(rec_buff.decode())
            if AT_FLAG:
                GPIO.output(green_led, GPIO.HIGH)
                AT_FLAG = False

            if not noti_flag:
                raw = str(rec_buff.decode())
                raw = raw[21:].split(",")
                if raw != ['']:
                    msg = raw[3] + "," + raw[4]
                    print(msg)
            return 1
    else:
        print('GPS is not ready')
        print("HERE 1")
        return 0

def get_gps_position():
    rec_null = True
    answer = 0
    print('Start GPS session...')
    global rec_buff

    if rec_null:
        print(">>>>")
        answer = send_at('AT+CGNSINF', '+CGNSINF: ', 1)
        print("<<<<")
        if answer == 1:
            answer = 0
            if ',,,,,,' in rec_buff.decode():
                print('GPS is not ready')
                print("HERE 2")
                rec_null = False
                sleep(1)
        else:
            print(f'error {answer}')
            rec_buff = ''
            send_at('AT+CGPS=0', 'OK', 1)
            return False
        sleep(1)

def power_on(power_key):
    print('SIM7000X is starting:')
    GPIO.setwarnings(False)
    ser.flushInput()
    print('SIM7000X is ready')
    send_at('AT', 'OK', 1)
    gps_power("on")

def power_down(power_key):
    print('SIM7000X is logging off:')
    gps_power("off")
    print('Good bye')

def gps_power(state):
    if state == "on":
        send_at('AT+CGNSPWR=1', 'OK', 1)
    elif state == "off":
        send_at('AT+CGNSPWR=0', 'OK', 1)
    else:
        print("Invalid state !!!")
    sleep(1)

def send_text(name, num, msg, hos):
    print(msg)
    print(hos)
    text = f'''ID : 12345678
Name : Sam
Blood Group : O+
Accident_Path : https://www.google.co.in/maps/dir/{hos[0]},{hos[1]}/{msg[0]},{msg[1]}/'''
    print(text)
    main_sms(text, num)

def send_text_rel(num, msg, hos_name, hos_ph, pol_name, pol_ph):
    text = f'''ID : 12345678
Name : Sam
Blood Group : O+
Accident_Path : https://www.google.co.in/maps/place/{msg[0]},{msg[1]}
Hospital_Phone:{hos_ph}
Police_Phone:{pol_ph}
'''
    print(text)
    main_sms(text, num)

def button_check():
    while True:
        if GPIO.input(18) == GPIO.HIGH:
            print("1")
        else:
            print("0")
        sleep(0.5)

def close_hos(data, la, lo):
    for c, x in enumerate(data):
        coords_1 = (float(la), float(lo))
        coords_2 = (x[1][0], x[1][1])
        d = geopy.distance.geodesic(coords_1, coords_2)
        p = f"{d}"
        q = p.replace(" km", "")
        x.append(float(q))
    low_dis = data[0][3]
    index = 0
    for c, x in enumerate(data):
        if x[3] < low_dis:
            low_dis = x[3]
            index = c
    print(f"\n\nNearest Hospital: {data[index][0]} \nContact : {data[index][2]} \nDistance : {low_dis} km")
    return data[index][0], data[index][2], data[index][1]

def close_pol(data, la, lo):
    for c, x in enumerate(data):
        coords_1 = (float(la), float(lo))
        coords_2 = (x[1][0], x[1][1])
        d = geopy.distance.geodesic(coords_1, coords_2)
        p = f"{d}"
        q = p.replace(" km", "")
        x.append(float(q))
    low_dis = data[0][3]
    index = 0
    for c, x in enumerate(data):
        if x[3] < low_dis:
            low_dis = x[3]
            index = c
    print(f"\n\nNearest Police station: {data[index][0]} \nContact : {data[index][2]} \nDistance : {low_dis} km")
    return data[index][0], data[index][2], data[index][1]

def trigger_case(case):
    global acci_time, flag
    print(f"Accident due to {case}")
    acci_time = time()
    flag = False
    output_device(True)
    print("\n")

def output_device(state):
    if state == True:
        GPIO.output(red_led, GPIO.HIGH)
    elif state == False:
        GPIO.output(red_led, GPIO.LOW)
        GPIO.output(green_led, GPIO.LOW)
    else:
        GPIO.output(red_led, GPIO.LOW)

power_on(power_key)  # Power SIM7000

try:
    while True:
        if flag:
            # Read Accelerometer raw values
            acc_x = read_raw_data(ACCEL_XOUT_H)
            acc_y = read_raw_data(ACCEL_YOUT_H)
            acc_z = read_raw_data(ACCEL_ZOUT_H)

            # Read Gyroscope raw values
            gyro_x = read_raw_data(GYRO_XOUT_H)
            gyro_y = read_raw_data(GYRO_YOUT_H)
            gyro_z = read_raw_data(GYRO_ZOUT_H)

            temp = (read_raw_data(TEMP_OUT0) / 340.0) + 36.53

            # Full scale range +/- 250 degree/C as per sensitivity scale factor
            Ax = acc_x / 16384.0
            Ay = acc_y / 16384.0
            Az = acc_z / 16384.0

            Gx = gyro_x / 131.0
            Gy = gyro_y / 131.0
            Gz = gyro_z / 131.0

            print(("\n" + 
                f"Gx={Gx:.2f}°/s\tGy={Gy:.2f}°/s\tGz={Gz:.2f}°/s\t"
                f"Ax={Ax:.2f} g\tAy={Ay:.2f} g\tAz={Az:.2f} g\t"
                f"T={temp:.2f}°C").encode('utf-8'))

            if Gy >= 10.0:
                print("Accident due to Gy1")
            if Gy <= -10.0:
                print("Accident due to Gy2")
            if Gx >= 10.0:
                print("Accident due to Gx1")
            if Gx <= -10.0:
                print("Accident due to Gx2")
            if Ax > 0.75:
                trigger_case("Ax1")
            if Ax < -0.75:
                trigger_case("Ax2")
            if Ay > 0.35:
                trigger_case("Ay1")
            if Ay < -0.35:
                trigger_case("Ay2")

        elif noti_flag:
            ta = timer - (time() - acci_time)
            sys.stdout.write("\r")
            sys.stdout.write(f"Remaining seconds to Trigger: {round(ta, 0)}")
            sys.stdout.flush()

            if GPIO.input(no_help_but) == GPIO.HIGH:
                buttonState = 1

            if buttonState == 1 and time() - acci_time <= timer:
                flag = True
                buttonState = 0
                output_device("Restart")
                print("\n\nRestarting the module in 1sec")
                sleep(1)

            if time() - acci_time > timer and noti_flag:
                noti_flag = False
                print("\nAccident happened and notification is triggered")
                print("\nNotification Sent to: ")

                get_gps_position()

                msg_parts = msg.split(",")

                try:
                    hos_name, hos_num, hos_lo = close_hos(data, la=float(msg_parts[0]), lo=float(msg_parts[1]))
                    pol_name, pol_num, pol_lo = close_pol(data_police, la=float(msg_parts[0]), lo=float(msg_parts[1]))
                except Exception as e:
                    print("GPS don't have NETWORK !!!")
                    hos_name, hos_num, hos_lo = close_hos(data, la=0.00, lo=0.00)
                    pol_name, pol_num, pol_lo = close_pol(data_police, la=0.00, lo=0.00)
                    msg_parts = [0.00, 0.00]
                    hos_lo = [0.00, 0.00]
                    pol_lo = [0.00, 0.00]

                send_text(hos_name, hos_num, msg_parts, hos_lo)
                sleep(2)
                send_text(pol_name, pol_num, msg_parts, pol_lo)
                sleep(3)
                send_text_rel(em_pho_no, msg_parts, hos_name, hos_num, pol_name, pol_num)

        if not noti_flag:
            print("\n Shutting down...., Restart the module/car!!! ")
            output_device(False)
            exit(0)

        sleep(0.1)

except KeyboardInterrupt:
    print("\n Shutting down...., Restart the module/car!!! ")
    output_device(False)
    exit(0)
