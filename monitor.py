from smbus import SMBus
import pigpio
import time
import board
import busio
from adafruit_htu21d import HTU21D
import sqlite3


#MPL3115A2 is chip_1
#HTU21D is chip_2

class Chip_1():
    def __init__(self):
        self.bus = SMBus(1)
        self.ADDR = 0x60

    def define_registers(self):
        self.bus.write_byte_data(self.ADDR, 0x26, 0xB9)
        self.bus.write_byte_data(self.ADDR, 0x13, 0x07)
        self.bus.write_byte_data(self.ADDR, 0x26, 0xB9)
        time.sleep(1)

    def convert_to_20(self):
        return ((self.data[1] * 65536) +
                (self.data[2] * 256) + (self.data[3] & 0xF0)) / 16

    def control_reg_reset(self):
        self.bus.write_byte_data(0x60, 0x26, 0x39)
        time.sleep(1)

    def read_temp(self, type='c'):
        self.define_registers()

        self.data = self.bus.read_i2c_block_data(self.ADDR, 0x00, 6)
        temp = ((self.data[4] * 256) + (self.data[5] & 0xF0)) / 16
        c_temp = temp / 16
        if type == 'c':
            return c_temp
        elif type == 'f':
            return c_temp * 1.8 + 32

    def read_alt(self, type='m'):
        self.define_registers()
        self.data = self.bus.read_i2c_block_data(self.ADDR, 0x00, 6)
        alt = self.convert_to_20() / 16
        if type == 'm':
            return alt
        elif type == 'f':
            return alt * 3.281

    def read_pressure(self, type='kpa'):
        self.control_reg_reset()
        self.data = self.bus.read_i2c_block_data(self.ADDR, 0x00, 6)
        pressure = (self.convert_to_20() / 4) / 1000
        if type == 'kpa':
            return pressure
        elif type == 'psi':
            return pressure / 6.895


class Chip_2():
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = HTU21D(self.i2c)

    def read_rh(self):
        time.sleep(.5)
        return self.sensor.relative_humidity



def store_data(conn, temp, alt, press, hum):
    ts = time.time()
    c = conn.cursor()
    c.execute("""INSERT INTO house_data
        (ts, temperature, altitude, pressure, humidity)
        values (?,?,?,?,?)""",
        (ts, temp, alt, press, hum))
    conn.commit()



if __name__ == '__main__':
    a = Chip_1()
    h = Chip_2()
    conn = sqlite3.connect('db/data.db')
    while True:
        temp = round(a.read_temp(type='f'), 2)
        alt = round(a.read_alt(type='f'), 2)
        press = round(a.read_pressure(type='psi'), 2)
        rh = round(h.read_rh(), 2)
        store_data(conn, temp, alt, press, rh)
        time.sleep(60)
