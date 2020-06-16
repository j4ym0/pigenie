import os
import time
import logger
import energenie
import shutil

class Display():
    statement  = 'PIGenie by J4yM0 (alpha release)'
    socket_s   = ''
    emon_s     = ''
    usage_s    = ''
    start_time = time.time()

    intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),    # 60 * 60 * 24
            ('hours', 3600),    # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )

    def human_time(self, seconds, granularity=4):
        result = []

        for name, count in self.intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{0:.3g} {1}".format(value, name))
        return ', '.join(result[:granularity])

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def spacer(self):
        columns, rows = shutil.get_terminal_size()
        return '-' * columns

    def emons_update(self, devices):
        self.emon_s = '\n'.join(['Monitors', self.spacer()])
        for d in devices:
            try:
                GENORATION = 0
                if d.product_id == energenie.Devices.PRODUCTID_MIHO006:
                    # work out the power factor for later
                    pf = ((d.get_current()/240)*d.get_apparent_power())
                    # working out the watts = amps x volts
                    GENORATION =(240*d.get_current())/(0.84) # device by power factor
                    # if less than 1 watt this can be 0 as may just be the power for the meater
                    # digital meaters can use up to 3wh

                    # print data for device
                    self.emon_s = '\n'.join([self.emon_s, "\tGenerating: %.2fKw/h, Battery: %.0f%%" % (GENORATION/1000, d.get_battery_life())])
            except Exception as e:
                logger.warning(e) # print exception

    def sockets_update(self, sockets, socket_cfg):
        self.socket_s = '\n'.join(['Socket Status', self.spacer()])
        for socket in socket_cfg:
            self.socket_s = '\n'.join([self.socket_s, ''.join(['\tSocket ', str(socket['socket']), ': ', 'on' if sockets[socket['socket']].get_last_state() is True else 'off'])])

    def usage_update(self, genarating, using):
        self.usage_s = 'Generating: %.2fKw/h, Consuming: %.2fKw/h' % (genarating/1000, using/1000)

    def render(self, level = 1):
        if level > 1: return
        self.clear_screen()
        uptime = 'Uptime : %s ' % self.human_time(time.time() - self.start_time)
        pr = '\n\n\n'.join([self.statement, '\n'.join([self.usage_s, uptime]), self.emon_s, self.socket_s,])
        print(pr)
