import logging
import time
from .display import menu_keys


class E3v3seDisplay:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.mutex = self.printer.get_reactor().mutex()
        self.name = config.get_name()
        self.reactor = self.printer.get_reactor()
        self._logging = config.getboolean("logging", False)
        self.gcode = self.printer.lookup_object("gcode")
        self.printer.register_event_handler("klippy:ready", self.handle_ready)

        # register for key events
        menu_keys.MenuKeys(config, self.key_event)

        self._update_interval = 1
        self._update_timer = self.reactor.register_timer(self._screen_update)

    def key_event(self, key, eventtime):
        if key == 'click':
            self.log("click pressed.")
        elif key == 'long_click':
            self.log("long_click pressed.")
        elif key == 'up':
             self.log("up pressed ")
        elif key == 'down':
             self.log("down pressed ")

    def _screen_update(self, eventtime):
        #self.log("Display update: ")
        return eventtime + self._update_interval

    def _screen_init(self, eventtime):
        self.reactor.update_timer(
            self._update_timer, eventtime + self._update_interval)
        return self.reactor.NEVER

    def handle_ready(self):
        self.reactor.register_timer(
            self._reset_screen, self.reactor.monotonic())
        
    def _reset_screen(self, eventtime):
        self.log("Reset")
        self.reactor.register_timer(
            self._screen_init, self.reactor.monotonic() + 2.)
        return self.reactor.NEVER

    def log(self, msg, *args, **kwargs):
        if self._logging:
            logging.info("E3V3SE Display: " + str(msg))

    def error(self, msg, *args, **kwargs):
        logging.error("E3V3SE Display: " + str(msg))

    def get_encoder_state(self):
        return self.encoder.getValue()

def load_config(config):
    return E3v3seDisplay(config)

