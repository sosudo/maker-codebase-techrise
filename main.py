# Import required modules and libraries
import board
import neopixel
import trsim_aerostar
import busio
import digitalio
import adafruit_sdcard
import storage
import analogio
from radiation import Radiation

# Set up variables for timer trigger
timr = 99999
trig = 90
inc = 0
incL = 10
incF = 30

# Create instances of AnalogIn and DigitalInOut for both geiger counters
sensor_pin_1 = analogio.AnalogIn(board.A4)
ns_pin_1 = digitalio.DigitalInOut(board.D12)
ns_pin_1.switch_to_input(pull=digitalio.Pull.DOWN)
'''
sensor_pin_2 = analogio.AnalogIn(board.A3)
ns_pin_2 = digitalio.DigitalInOut(board.D1)

ns_pin_2.switch_to_input(pull=digitalio.Pull.DOWN)
'''
sensor_pin_3 = analogio.AnalogIn(board.A2)
ns_pin_3 = digitalio.DigitalInOut(board.D4)
ns_pin_3.switch_to_input(pull=digitalio.Pull.DOWN)
sensor_pin_4 = analogio.AnalogIn(board.A1)
ns_pin_4 = digitalio.DigitalInOut(board.D13)
ns_pin_4.switch_to_input(pull=digitalio.Pull.DOWN)

# Create instances of the Radiation class for both geiger counters
rad_1 = Radiation(sensor_pin_1, ns_pin_1)
'''
rad_2 = Radiation(sensor_pin_2, ns_pin_2)
'''
rad_3 = Radiation(sensor_pin_3, ns_pin_3)
rad_4 = Radiation(sensor_pin_4, ns_pin_4)

# Set up for SD breakout board
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D7)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# SPI Flash
bit = board.D6

# Connect to Bitflip Pins
'''
bspi = busio.SPI(board.SCK, board.MOSI, board.MISO)
bcs = digitalio.DigitalInOut(bit)
b = SPIDevice(bspi, bcs)
'''

# Write CSV headers
with open("/sd/SDtest.txt", "a") as f:
    f.write("Time" + "," + "Latitude" + "," + "Longitude" + "," + "Altitude" +
            "," + "Rad 1" + "," + "Rad 2"  + "Rad 3," + "Rad 4," + "Bitflips\n")

with open("/sd/array.txt", "w") as f:
    for _ in range(10000):
        f.write('0')

print("Running STAR 16 flight code")

# ByteArray
_bytearray = [0 for _ in range(10000)]


# Set up Neopixel hardware constants and object for the M4's on-board Neopixel
NEOPIXEL_PIN = board.NEOPIXEL
NEOPIXEL_COUNT = 1
NEOPIXEL_BRIGHTNESS = 0.2
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_COUNT, brightness=NEOPIXEL_BRIGHTNESS)

# Set up some basic color constants for use later
COLOR_RED = const(0xff0000)
COLOR_GREEN = const(0x00ff00)
COLOR_BLUE = const(0x0000ff)
COLOR_YELLOW = const(0xffff00)
COLOR_MAGENTA = const(0xff00ff)
COLOR_CYAN = const(0x00ffff)
COLOR_BLACK = const(0x000000)
COLOR_GRAY = const(0x7f7f7f)
COLOR_WHITE = const(0xffffff)

# Set up flight status event Neopixel colors index
status_colors = [None] * trsim_aerostar.STATUS_NUM_EVENTS
status_colors[trsim_aerostar.STATUS_UNKNOWN] = COLOR_GRAY
status_colors[trsim_aerostar.STATUS_INITIALIZING] = COLOR_YELLOW
status_colors[trsim_aerostar.STATUS_LAUNCHING] = COLOR_GREEN
status_colors[trsim_aerostar.STATUS_FLOATING] = COLOR_CYAN
status_colors[trsim_aerostar.STATUS_DESCENDING] = COLOR_BLUE


# Set up simulator data library
#   By default, PBF pin = 2, GO pin = 3. If your wiring is different, see
#   documentation for how to change pins using this function call.
TRsim = trsim_aerostar.Simulator()

# Initialize flight status
curr_status = trsim_aerostar.STATUS_UNKNOWN
prev_status = curr_status

# Display flight status (unknown) on Neopixel
pixels.fill(status_colors[curr_status])

# Variable for tracking number of full telemetry packets received
num_packets = 0

# START THE MAIN LOOP
while True:
    # Call Simulator update() function to catch serial input and check PBF.
    #   This must be called at the top of the loop.
    TRsim.update()

    # Check if the PBF header is closed (False). If it is, light Neopixel red.
    #   If it is open (True), we are free to do in-flight work!
    if TRsim.pbf is False:
        # Light the neopixel red to highlight that the PBF is inserted
        pixels.fill(COLOR_RED)
    else:
        # PBF header is open, we are flying and can do some work!

        # TRsim.streaming will be True while valid data is incoming
        # If data is paused for more than 1.5 seconds it will become False
        if TRsim.streaming:
            # TRsim.new_data will be True after a new packet arrives
            # When TRsim.data is called TRsim.new_data will become False.
            if TRsim.new_data:
                # Got a new telemetry packet, let's count it!
                num_packets += 1

                # Grab new data - NOTE this sets new_data to False
                data = TRsim.data

                # You can add code here that needs to execute each time new
                #   telemetry data is received.

                # Get current flight status and check to see if it has changed
                curr_status = TRsim.status
                # See if the status has changed by comparing with previous value
                if curr_status != prev_status:
                    # If it has changed, save the current status to prev_status
                    prev_status = curr_status
                    # Since the event changed, print something to indicate change.
                    # You can initiate activity for your payload in this
                    #   section, since it will only execute on status change.
                    #   However, when running the simulator, please note that
                    #   this section may execute again if you pause and unpause
                    #   the simulator.
                    if curr_status == trsim_aerostar.STATUS_INITIALIZING:
                        print("We are initializing")
                        timr = TRsim.time_secs + 99999
                    elif curr_status == trsim_aerostar.STATUS_LAUNCHING:
                        print("We are launching")
                        inc = incL
                        timr = TRsim.time_secs + trig
                    elif curr_status == trsim_aerostar.STATUS_FLOATING:
                        print("We are floating")
                        inc = incF
                    elif curr_status == trsim_aerostar.STATUS_DESCENDING:
                        print("We are descending")
                        inc = incF
                    # Indicate the new event with a color from the status list
                    pixels.fill(status_colors[curr_status])

                # Print every 1000th packet to verify data
                if (num_packets % 1000) == 1:
                    TRsim.print_current_packet()

            if TRsim.time_secs > timr:
                total_uSv_h_1 = rad_1.get_total_radiation()
                total_uSv_h_2 = rad_1.get_total_radiation()
                #total_uSv_h_2 = 0
                total_uSv_h_3 = rad_3.get_total_radiation()
                total_uSv_h_4 = rad_4.get_total_radiation()
                TRsim.update()
                flips = []
                #b.readinto(flips)
                num = 0
                '''
                for i in range(50000):
                    if _bytearray[i] != flips[i]:
                        num += 1
                print(TRsim.altitude)
                '''
                with open("/sd/array.txt", "r") as f:
                    for i in f:
                        flips.append(int(i))

                for i in range(min(len(_bytearray), len(flips))):
                    if _bytearray[i] != flips[i]:
                        num += 1

                with open("/sd/SDtest.txt", "a") as f:
                    f.write("{},{},{},{},{},{},{},{},{}\n".
                            format(TRsim.time_secs, TRsim.latitude, TRsim.longitude,
                                   TRsim.altitude, total_uSv_h_1, total_uSv_h_2,
                                   total_uSv_h_3, total_uSv_h_4, num))
                timr = TRsim.time_secs + inc
                num = 0
                _bytearray = [i for i in flips]
                print(timr)

        else:
            pixels.fill(COLOR_RED)
            # Data stream has stopped for 1.5s, fill pixels with unknown (idle) color
            pixels.fill(status_colors[trsim_aerostar.STATUS_UNKNOWN])

            # Reset the previous status to unknown (idle)
            prev_status = trsim_aerostar.STATUS_UNKNOWN
