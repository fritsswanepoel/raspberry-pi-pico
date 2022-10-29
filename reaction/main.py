#Packages
from machine import Pin
import utime
import urandom

#Variables
start = False
game = 1

min_time = 1
max_time = 5

min_time2 = 3
max_time2 = 7

indicator_loops = 50
indicator_sleep = 15

#Components
game_button = Pin(22, Pin.IN, Pin.PULL_DOWN)

left_button = Pin(20, Pin.IN, Pin.PULL_DOWN)
right_button = Pin(16, Pin.IN, Pin.PULL_DOWN)
control_button = Pin(18, Pin.IN, Pin.PULL_DOWN)


left_led = Pin(11, Pin.OUT)
right_led = Pin(15, Pin.OUT)
control_led = Pin(13, Pin.OUT)

buzzer = Pin(9, Pin.OUT)

pressed_latest = {}
latest_switch = utime.ticks_ms()

#Functions
def switch_game_handler(pin):
    global latest_switch
    #print(utime.ticks_diff(utime.ticks_ms(), latest_switch))
    if utime.ticks_diff(utime.ticks_ms(), latest_switch) > 2000:
        print("switch")
        global game
        game = game *-1
        control_led.value(1)
        utime.sleep(0.3)
        control_led.value(0)
        latest_switch = utime.ticks_ms()
    
    
def early_button_handler(pin):
    global pressed_early
    if not pressed_early:
        pressed_early=True
        global fastest_button_early
        fastest_button_early = pin


def latest_button_handler(pin):
    if pin == left_button:
        button = 'left'
    else:
        button = 'right'

    if button not in pressed_latest.keys():
        pressed_latest[button] = utime.ticks_ms()

def button_handler(pin):
    global pressed
    global timer_reaction
    if not pressed:
        pressed=True
        timer_reaction = utime.ticks_diff(utime.ticks_ms(), timer_start)
        global fastest_button
        fastest_button = pin

def start_handler(pin):
    global start
    start = True

def winner(led):
    for t in range(indicator_loops):
        led.toggle()
        control_led.toggle()
        utime.sleep_ms(indicator_sleep)
    led.value(0)
    control_led.value(0)
    
def too_early(led):
    control_led.toggle()
    for t in range(indicator_loops):
        buzzer.toggle()
        led.toggle()
        control_led.toggle()
        utime.sleep_ms(indicator_sleep)
    control_led.value(0)
    led.value(0)

def too_late():
    control_led.toggle()
    for t in range(indicator_loops):
        buzzer.toggle()
        left_led.toggle()
        right_led.toggle()
        control_led.toggle()
        utime.sleep_ms(indicator_sleep)
    control_led.value(0)
    left_led.value(0)
    right_led.value(0)

while True:
    game_button.irq(trigger=Pin.IRQ_RISING, handler=switch_game_handler)
    #print(game)
    control_button.irq(trigger=Pin.IRQ_RISING, handler=start_handler)
    if start:
        if game == 1:
            #Variables
            pressed = False
            pressed_early = False
            timer_reaction = None
            timer_start = None
            fastest_button = None
            fastest_button_early = None

            #Main body
            control_led.value(1)
            target_time = utime.ticks_add(utime.ticks_ms(), int(urandom.uniform(min_time, max_time)*1000))

            #Check if a player presses too early
            while utime.ticks_diff(target_time, utime.ticks_ms()) >= 0:
                left_button.irq(trigger=Pin.IRQ_RISING, handler=early_button_handler)
                right_button.irq(trigger=Pin.IRQ_RISING, handler=early_button_handler)
                if pressed_early:
                    control_led.value(0)
                    target_time=0

            #If not pressed early
            if not pressed_early:
                control_led.value(0)
                timer_start = utime.ticks_ms()
                left_button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)
                right_button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)

            #Print results
            while fastest_button is None and fastest_button_early is None:
                utime.sleep(1)
            if fastest_button is left_button:
                print(f"Left player wins. Reacted in {timer_reaction} milliseconds")
                winner(left_led)
            elif fastest_button_early is left_button:
                print("Left player jumped the gun")
                too_early(left_led)
            elif fastest_button is right_button:
                print(f"Right player wins. Reacted in {timer_reaction} milliseconds")
                winner(right_led)
            elif fastest_button_early is right_button:
                print("Right player jumped the gun")
                too_early(right_led)
        
        else:
            #Variables
            pressed_early = False
            timer_reaction = None
            timer_start = None
            fastest_button_early = None

            #Main body
            control_led.value(1)
            left_target_time = utime.ticks_add(utime.ticks_ms(), int(urandom.uniform(min_time2, max_time2)*1000))
            right_target_time = utime.ticks_add(utime.ticks_ms(), int(urandom.uniform(min_time2, max_time2)*1000))

            #Check if a player presses too early
            while utime.ticks_diff(max(left_target_time, right_target_time), utime.ticks_ms()) >= 0:
                left_button.irq(trigger=Pin.IRQ_RISING, handler=latest_button_handler)
                right_button.irq(trigger=Pin.IRQ_RISING, handler=latest_button_handler)
 
            control_led.value(0)
            
            left_time = left_target_time - pressed_latest.get('left',utime.ticks_ms())
            right_time = right_target_time - pressed_latest.get('right',utime.ticks_ms())
            

            #Results
            if len(pressed_latest) == 0:
                too_late()
            elif left_time < right_time:
                print("Left player was closest")
                winner(left_led)
            elif right_time < left_time:
                print("Right player was closest")
                winner(right_led)

        control_led.value(0)
        left_led.value(0)
        right_led.value(0)
        start = False
        pressed_latest = []
        
    else:
        utime.sleep(1)