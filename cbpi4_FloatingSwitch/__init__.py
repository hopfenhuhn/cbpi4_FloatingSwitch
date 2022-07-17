
# -*- coding: utf-8 -*-
import asyncio
import logging
from unittest.mock import MagicMock, patch

from cbpi.api import *


logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except Exception:
    logger.error("Failed to load RPi.GPIO. Using Mock")
    MockRPi = MagicMock()
    modules = {
        "RPi": MockRPi,
        "RPi.GPIO": MockRPi.GPIO
    }
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    import RPi.GPIO as GPIO


@parameters([Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]),
             Property.Select(label="Direction", options=["low", "high"], description="Switch active on GPIO high or low (default: low)"),
             Property.Actor(label="Dashboard-LED", description="Chose dummy-actor for dashboard LED if switch is triggered.")])
class FloatingSwitch(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(FloatingSwitch, self).__init__(cbpi, id, props)
        self.value = 0
        self.gpio = self.props.GPIO
        self.direction = GPIO.HIGH if self.props.get("Direction", "low") == "high" else GPIO.LOW
        self.dashboardled = self.props.get("Dashboard-LED", None)
        actor_led = self.cbpi.actor.find_by_id(self.dashboardled)

        try:
            GPIO.setup(int(self.gpio),GPIO.IN)
            GPIO.remove_event_detect(int(self.gpio))
#            GPIO.add_event_detect(int(self.gpio), self.direction, callback=self.isFull, bouncetime=100)
        except Exception as e:
            print(e)

#    def isFull(self, channel):
#        self.value = 1

    async def run(self):
        while self.running is True:
            try:
                actor_led_state = actor_led.instance.state
            except:
                actor_led_state = False

            if GPIO.input(self.gpio) == self.direction:
                self.value = 1
                self.push_update(self.value)
                if actor_led_state == False:
                    await self.cbpi.actor.on(self.dashboardled)
                    #self.state = True
                #await asyncio.sleep(5)
            else:
                self.value = 0
                self.push_update(self.value)
                #if actor_led_state == True:
                await self.cbpi.actor.off(self.dashboardled)
                    #self.state = False
            await asyncio.sleep(1)

    def get_state(self):
        return dict(value=self.value)


@parameters([Property.Actor(label="Pump",  description="Select the actor you would like to add a dependency to."),
             Property.Sensor(label="SensorDependency", description="Select the sensor that the base actor will depend upon."),
             Property.Number(label="Time", description="Time in seconds the actor will be triggered for pumping wort.")])

class TimedPump(CBPiActor):
    def on_start(self):
        self.state = False
        self.pump = self.props.get("Pump", None)
        self.sensor_dependency = self.props.get("SensorDependency", None)
        self.time = self.props.get("Time", 0)
        pump_actor = self.cbpi.actor.find_by_id(self.pump)
        sensor_dep = self.cbpi.sensor.find_by_id(self.sensor_dependency)
        self.init = False
        pass

    async def on(self, power=None):
        #sensor_val = self.cbpi.sensor.get_sensor_value(self.sensor_dependency).get("value")
        #logger.info("Schwimmerschalter Status %s" % sensor_val)
        self.state = True
        while self.state is True:
            sensor_val = self.cbpi.sensor.get_sensor_value(self.sensor_dependency).get("value")
            #logger.info("Schwimmerschalter Status %s" % sensor_val)
            if sensor_val == 1:
                await self.cbpi.actor.on(self.pump)
                await asyncio.sleep(self.time)
            else:
                 await self.cbpi.actor.off(self.pump)
                 await asyncio.sleep(1)

    async def off(self):
        logger.info("ACTOR %s OFF " % self.pump)
        await self.cbpi.actor.off(self.pump)
        self.state = False

    def get_state(self):
        return self.state

    async def run(self):

        # if self.init == False:
        #     if self.pump is not None:
        #         await self.cbpi.actor.off(self.pump)
        #         self.state = False
        #     self.init = True
        pass

def setup(cbpi):
    cbpi.plugin.register("FloatingSwitch", FloatingSwitch)
    cbpi.plugin.register("TimedPump", TimedPump)
    #cbpi.plugin.register("MyCustomActor", CustomActor)
    #cbpi.plugin.register("MyCustomSensor", CustomSensor)
    #cbpi.plugin.register("MyustomWebExtension", CustomWebExtension)
    pass
