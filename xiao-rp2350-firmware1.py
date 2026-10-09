import time
from machine import Pin, I2C
import ssd1306
ROW_PINS =[6,11,12]
COL_PINS =[1,2,3]
ENC_A=0
ENC_B=14
encoder_a = Pin(ENC_A, Pin.IN, Pin.PULL_UP)
encoder_b = Pin(ENC_B, Pin.IN, Pin.PULL_UP)
rows = [Pin(pin, Pin.OUT) for pin in ROW_PINS]
cols = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in COL_PINS]
selected_timer=-1
active = True
mute = False

i2c = I2C(
    0,
    scl=Pin(5),
    sda=Pin(4),
    freq=400000
)

oled = ssd1306.SSD1306_I2C(128, 32, i2c)
class Timer:
    def __init__(self):
        self.hr=1
        self.min=0
        self.sec=0
    def get_time(self):
        return f"{self.hr}:{self.min:02}:{self.sec:02}"
    def set_time(self,hour,minute,second):
        self.hr=hour
        self.min=minute
        self.sec=second
    def change(self):
        if self.sec>0:
            self.sec-=1
            return(False)
        elif self.min >0:
            self.min-=1
            self.sec+=59
            return(False)
        elif self.hr >0:
            self.hr-=1
            self.min+=59
            self.sec+=59
            return(False)
        else:
            return(True)
timers = [Timer() for _ in range(8)]
def scan_matrix():
    for row in range(3):

        # Set every row HIGH
        for r in rows:
            r.value(0)

        # Activate this row
        rows[row].value(1)

        # Check each column
        for col in range(3):
            if cols[col].value() == 1:
                return row+3*col

    return -1
def set_timer_with_encoder():
    hour = 0
    minute = 0
    second = 0

    selected = 0

    last_a = encoder_a.value()
    selected_timer = -1

    while True:

        current_a = encoder_a.value()

        if current_a != last_a:

            if encoder_b.value() != current_a:
                direction = 1      
            else:
                direction = -1      

            if selected == 0:
                hour += direction
                hour %= 24

            elif selected == 1:
                minute += direction
                minute %= 60

            elif selected == 2:
                second += direction
                second %= 60

            oled.text(f"{hour}:{minute:02}:{second:02}",0,0)
            oled.show

        last_a = current_a


        button = scan_matrix()


        if button == 6 and selected_timer != 6:

   
            if selected < 2:
                selected += 1
                time.sleep_ms(200)

        elif 0 <= button <= 5 and selected_timer != button:

            timers[button].set_time(hour, minute, second)

            print(
                f"Timer {button + 1} set to "
                f"{hour}:{minute:02}:{second:02}"
            )

            return

        selected_timer = button
while True:
    if(scan_matrix() != -1):
        selected_timer=scan_matrix()
    if selected_timer ==8:
        mute = not mute
        selected_timer =-1
    elif selected_timer ==2:
        active = not active
        selected_timer = -1
    elif selected_timer ==6:
        set_timer_with_encoder()
    else:
        while(active):
            oled.text(timers[selected_timer].get_time(),0,0)
            oled.show
            if(timers[selected_timer].change()):
                oled.text("Done",0,0)
            
            
            
