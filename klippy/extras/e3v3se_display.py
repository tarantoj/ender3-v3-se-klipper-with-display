import logging
import time
from .display import menu_keys
from .TJC3224 import TJC3224_LCD

class E3v3seDisplay:
    
    ENCODER_DIFF_NO = 0  # no state
    ENCODER_DIFF_CW = 1  # clockwise rotation
    ENCODER_DIFF_CCW = 2  # counterclockwise rotation
    ENCODER_DIFF_ENTER = 3  # click

    # Color Palette
    color_white = 0xFFFF
    color_yellow = 0xFF0F
    color_popup_background = 0x31E8  # Popup background color
    color_background_grey = 0x1145  # Dark grey background color
    color_background_black = 0x0841  # Black background color
    color_background_red = 0xF00F  # Red background color
    color_popup_text = 0xD6BA  # Popup font_ background color
    color_line = 0x3A6A  # Split line color
    Rectangle_color = 0xEE2F  # Blue square cursor color
    Percent_color = 0xFE29  # Percentage color
    BarFill_color = 0x10E4  # Fill color of progress bar
    Selected_color = 0x33BB  # Selected color

    EncoderRateLimit = True

    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.mutex = self.printer.get_reactor().mutex()
        self.name = config.get_name()
        self.reactor = self.printer.get_reactor()
        self._logging = config.getboolean("logging", False)
        self.gcode = self.printer.lookup_object("gcode")
        self.printer.register_event_handler("klippy:ready", self.handle_ready)
        self.encoder_state = self.ENCODER_DIFF_NO

        # register for key events
        menu_keys.MenuKeys(config, self.key_event)

        bridge = config.get('serial_bridge')

        self.serial_bridge = self.printer.lookup_object(
            'serial_bridge %s' %(bridge))
        self.serial_bridge.register_callback(
            self._handle_serial_bridge_response)
        
        self.lcd = TJC3224_LCD(self.serial_bridge)

        self._update_interval = 1
        self._update_timer = self.reactor.register_timer(self._screen_update)

    def key_event(self, key, eventtime):
        if key == 'click':
            self.log("click")
            self.encoder_state = self.ENCODER_DIFF_ENTER
        elif key == 'long_click':
            self.log("long_click")
            self.encoder_state = self.ENCODER_DIFF_ENTER
        elif key == 'up':
            self.log("up")
            self.encoder_state = self.ENCODER_DIFF_CCW
        elif key == 'down':
            self.log("down")
            self.encoder_state = self.ENCODER_DIFF_CW

        self.encoder_has_data()

    def get_encoder_state(self):
        last_state = self.encoder_state
        self.encoder_state = self.ENCODER_DIFF_NO
        return  last_state

    def encoder_has_data(self):
        self.log("Key event")
    
    def _handle_serial_bridge_response(self, data):
        byte_debug = ' '.join(['0x{:02x}'.format(byte) for byte in data])
        self.log("Received message: " + byte_debug)
    
    def send_text(self, text):
        self.serial_bridge.send_text(text)

    def _screen_update(self, eventtime):
        self.log("Display update")
        return eventtime + self._update_interval

    def _screen_init(self, eventtime):
        self.reactor.update_timer(
            self._update_timer, eventtime + self._update_interval)
        return self.reactor.NEVER

    def handle_ready(self):
        self.reactor.register_timer(
            self._reset_screen, self.reactor.monotonic())
        
        self.HMI_ShowBoot()
        
    def _reset_screen(self, eventtime):
        self.log("Reset")
        self.reactor.register_timer(
            self._screen_init, self.reactor.monotonic() + 2.)
        return self.reactor.NEVER

    def HMI_ShowBoot(self):
        self.lcd.clear_screen(self.color_background_black)

        self.lcd.draw_string(
            False,
            self.lcd.font_8x8,
            self.color_white,
            self.color_background_black,
            55,
            20,
            "Klipper E3V3SE ",
        )
        self.lcd.draw_string(
            False,
            self.lcd.font_8x8,
            self.color_white,
            self.color_background_black,
            70,
            50,
            "display mod",
        )
        # Todo: QR
        self.lcd.draw_string(
            False,
            self.lcd.font_8x8,
            self.color_white,
            self.color_background_black,
            80,
            250,
            "Github: ",
        )
        self.lcd.draw_string(
            False,
            self.lcd.font_8x8,
            self.color_white,
            self.color_background_black,
            0,
            280,
            "jpcurti/klipper_E3V3SE_display_mod",
        )

    def log(self, msg, *args, **kwargs):
        if self._logging:
            logging.info("E3V3SE Display: " + str(msg))

    def error(self, msg, *args, **kwargs):
        logging.error("E3V3SE Display: " + str(msg))

def load_config(config):
    return E3v3seDisplay(config)

