## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.
##

import sys
import pathlib
import openocd
import shutil

serial ='13678/00110029'
KM = 0

def word2bytes(word):
    result = [(word) & 0xff, (word >> 8) & 0xff, (word >> 16) & 0xff, (word >> 24) & 0xff]
    return bytes(result)
 
def write_binary(ocd, address, binary):

    path = str(pathlib.Path(__file__).parent.absolute())
    command= f'program {path}\\{binary} verify 0x{address:x}'
    ocd.execute(command.replace('\\','/'))
 
if __name__ == '__main__':
    print('')
    print('Connecting to OPENOCD at <localhost:6666>')

    oocd = openocd.OpenOcd('localhost', 6666)

    try:
        oocd.connect()
    except Exception as e:
        sys.exit('Failed to connect to OpenOCD')

    # Disable RDP
    print('Unsecuring device...')
    oocd.execute('init')
    oocd.execute('reset halt')
    oocd.execute('stm32f1x unlock 0')
    oocd.reset()
    print('ok')

    # read UUID
    oocd.execute('init')
    oocd.execute('reset halt')

    print('Reading UUID...')
    UUID = oocd.read_memory(0x1FFFF7E8, 3, 32)
    print('done: %08x %08x %08x\n' % (UUID[0], UUID[1], UUID[2]))

    print('Preparing scooter data...')

    shutil.copy('data.bin','data_temp.bin')

    scooter_data = open('data_temp.bin','r+b')

    scooter_data.seek(0x20)
    scooter_data.write(serial.encode())
    scooter_data.seek(0x1b4)
    scooter_data.write(word2bytes(UUID[0]))
    scooter_data.seek(0x1b8)
    scooter_data.write(word2bytes(UUID[1]))
    scooter_data.seek(0x1bc)
    scooter_data.write(word2bytes(UUID[2]))
    scooter_data.seek(0x52)
    scooter_data.write(word2bytes(KM*1000))
    scooter_data.close()

    print('Flashing scooter data...')
    write_binary(oocd, 0x08000000, 'boot.bin')
    write_binary(oocd, 0x08001000, 'DRV221.bin')
    write_binary(oocd, 0x0800f800, 'data_temp.bin')
    print('ok')

    print('Reading UUID2...')
    UUID2 = oocd.read_memory(0x0800F9B4, 3, 32)
    print('done: %08x %08x %08x\n' % (UUID2[0], UUID2[1], UUID2[2]))

    # maybe a compare of UUID vs UUID2  to match 

    oocd.reset()
    oocd.shutdown()
