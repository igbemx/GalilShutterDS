# -*- coding: utf-8 -*-
#
# This file is part of the SoftiGalilShutter project
# Author: Igor Beinik
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Galil based beam shutter

"""

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(SoftiGalilShutter.additionnal_import) ENABLED START #
import time
import logging
from threading import Thread
import numpy
import sys
import string
if __name__ == '__main__':
    import gclib
else:
    import SoftiGalilShutter.gclib as gclib

# PROTECTED REGION END #    //  SoftiGalilShutter.additionnal_import

__all__ = ["SoftiGalilShutter", "main"]


class SoftiGalilShutter(Device):
    """

    **Properties:**

    - Device Property
        host
            - Galil host name or ip.
            - Type:'DevString'
        port
            - Galil port number.
            - Type:'DevShort'
    """
    # PROTECTED REGION ID(SoftiGalilShutter.class_variable) ENABLED START #
    @DebugIt()
    def _switch_to_ext_ctrl(self, close_pos=7500, open_pos=7000):
        try:
            print('Calling _switch_to_ext_ctrl..')
            o_pos = int(open_pos)
            c_pos = int(close_pos)
            # self.program = '#A;JS#B,@IN[1]=0;JS#C,@IN[1]=1;JP#A;\n#B;PA7000;BGA;AMA;EN;\n#C;PA7500;BGA;AMA;EN'
            self._init_motor()
            print('Initializing the motor, please wait..')
            program = f'#A;JS#B,@IN[1]=0;JS#C,@IN[1]=1;JP#A;\n#B;PA{o_pos};BGA;AMA;EN;\n#C;PA{c_pos};BGA;AMA;EN' # Enables OPEN/CLOSE via DI1
            self.g.GProgramDownload(program, '--max 3')
            self.g.GCommand('XQ')
            # time.sleep(2)
            self.set_state(DevState.INSERT)
            self._external_control = True
        except Exception as e:
            print(f'Error in _switch_to_ext_ctrl{e}')
            self.set_state(DevState.FAULT)
            self.g.GClose()

    def _init_motor(self):
        try:
            program = '#A;ACA= 1000000;DCA= 1000000;SPA= 200000;SH A;EN' # Setting up the parameters and turning ON
            self.g.GProgramDownload(program, '--max 3')
            self.g.GCommand('XQ')
            self.set_state(DevState.ON)
        except Exception as e:
            print(f'Error in _init_motor(): {e}')
            self.set_state(DevState.FAULT)
            self.g.GClose()

    def _stop_all(self):
        self.g.GCommand('AB 0') #Abort motion and program operation
        #self.g.GCommand('ST A')

    def _open_shutter(self):
        if self.get_state() not in [DevState.MOVING, DevState.OPEN]:
            try:
                self.set_state(DevState.MOVING)
                #self.g.GCommand('PA4500')
                self.g.GCommand('PA'+str(self._open_value))
                self.g.GCommand('BG A')
            except Exception as e:
                #self.g.GClose()
                self.set_state(DevState.FAULT)
                print('Error in Open():', e)

    def _close_shutter(self):
        if self.get_state() not in [DevState.MOVING, DevState.CLOSE]:
            try:
                self.set_state(DevState.MOVING)
                self.g.GCommand('PA'+str(self._close_value))
                self.g.GCommand('BG A')
            except Exception as e:
                #self.g.GClose()
                self.set_state(DevState.FAULT)
                print('Error in Close()', e)
        
    # PROTECTED REGION END #    //  SoftiGalilShutter.class_variable

    # -----------------
    # Device Properties
    # -----------------

    host = device_property(
        dtype='DevString',
        default_value="172.16.206.54"
    )

    port = device_property(
        dtype='DevShort',
        default_value=23
    )

    # ----------
    # Attributes
    # ----------

    abs_position = attribute(
        dtype='DevLong64',
        access=AttrWriteType.READ_WRITE,
        label="Abs position",
        unit="counts",
        max_value=2147483646,
        min_value=-2147483647,
        doc="Absolute position",
    )

    offset = attribute(
        dtype='DevLong64',
        access=AttrWriteType.READ_WRITE,
        label="Offset",
        unit="counts",
        max_value=3999,
        min_value=0,
        doc="Clockwise offset from the index marker to 0 deg.",
    )

    external_control = attribute(
        dtype='DevBoolean',
        label="External control",
        doc="True if the device is controlled via one of the digital inputs.",
    )

    open_value = attribute(
        dtype='DevLong',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        label="Open value",
        unit="counts",
        doc="The encoder value at which the shutter should open.",
    )

    close_value = attribute(
        dtype='DevLong',
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        label="Close value",
        unit="counts",
        doc="The encoder value at which the shutter should close.",
    )

    closing_tolerance = attribute(
        dtype='DevLong',
        access=AttrWriteType.READ_WRITE,
        label="Closing tolerance",
        max_value=500,
        min_value=0,
        doc="The tolerance to determine whether the shutter is open or closed.",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the SoftiGalilShutter."""
        Device.init_device(self)
        # PROTECTED REGION ID(SoftiGalilShutter.init_device) ENABLED START #
        self._abs_position = 0
        self._offset = 2100
        self._external_control = False
        self.current_position = 0
        self._open_value = 7000
        self._close_value = 7500
        self._closing_tolerance = 40
        try:
            self.g = gclib.py()
            print('gclib version:', self.g.GVersion())
            self.g.GClose()
            time.sleep(1)
            self.g.GOpen(self.host + ' --direct -s ALL')
            print('The controller info during init: ', self.g.GInfo())
            self.current_position = int(self.g.GCommand('TP'))
            print('The current position is: ', self.current_position)
            self.set_state(DevState.STANDBY)
            self._switch_to_ext_ctrl(
                close_pos=self._close_value,
                open_pos=self._open_value
            )
        except Exception as e:
            self.g.GClose()
            self.set_state(DevState.FAULT)
            print(f'Error in init_device: {e}')
        # PROTECTED REGION END #    //  SoftiGalilShutter.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(SoftiGalilShutter.always_executed_hook) ENABLED START #
        try:
            self.current_position = int(self.g.GCommand('TP'))
            if abs(self.current_position - self._open_value) < self._closing_tolerance:
                if self._external_control:
                    self.set_state(DevState.INSERT)
                else:
                    self.set_state(DevState.OPEN)
            elif abs(self.current_position - self._close_value) < self._closing_tolerance:
                if self._external_control:
                    self.set_state(DevState.INSERT)
                else:
                    self.set_state(DevState.CLOSE)
        except Exception as e:
            print(f'There was an exception in always_executed_hook: {e}')
            self.g.GClose()
            time.sleep(1)
            print('Reopenning of the connection to the controller..')
            self.g.GOpen(self.host + ' --direct -s ALL')
            self.set_state(DevState.FAULT)
        # PROTECTED REGION END #    //  SoftiGalilShutter.always_executed_hook

    # PROTECTED REGION ID(SoftiGalilShutter.read_attr_hardware) ENABLED START #
    # def read_attr_hardware(self):
    #     print('Calling read_attr_hardware..')
    #     """Method always executed before each reading of attributes."""
    #     try:
    #         self.current_position = int(self.g.GCommand('TP'))
    #         print('read_attr_hardware call.., current posiontion is: ', self.current_position)
    #         if abs(self.current_position - self._open_value) < self._closing_tolerance:
    #             if self._external_control:
    #                 self.set_state(DevState.INSERT)
    #             else:
    #                 self.set_state(DevState.OPEN)
    #         elif abs(self.current_position - self._close_value) < self._closing_tolerance:
    #             if self._external_control:
    #                 self.set_state(DevState.INSERT)
    #             else:
    #                 self.set_state(DevState.CLOSE)
    #     except Exception as e:
    #         print('There was an error in read_attr_hardware:', e)
    #         self.g.GClose()
    #     # PROTECTED REGION END #    //  SoftiGalilShutter.read_attr_hardware

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(SoftiGalilShutter.delete_device) ENABLED START #
        self.g.GClose()
        # PROTECTED REGION END #    //  SoftiGalilShutter.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_abs_position(self):
        # PROTECTED REGION ID(SoftiGalilShutter.abs_position_read) ENABLED START #
        """Return the abs_position attribute."""
        return self.current_position
        # PROTECTED REGION END #    //  SoftiGalilShutter.abs_position_read

    def write_abs_position(self, value):
        # PROTECTED REGION ID(SoftiGalilShutter.abs_position_write) ENABLED START #
        """Set the abs_position attribute."""
        pass
        # PROTECTED REGION END #    //  SoftiGalilShutter.abs_position_write

    def read_offset(self):
        # PROTECTED REGION ID(SoftiGalilShutter.offset_read) ENABLED START #
        """Return the offset attribute."""
        return self._offset
        # PROTECTED REGION END #    //  SoftiGalilShutter.offset_read

    def write_offset(self, value):
        # PROTECTED REGION ID(SoftiGalilShutter.offset_write) ENABLED START #
        """Set the offset attribute."""
        pass
        # PROTECTED REGION END #    //  SoftiGalilShutter.offset_write

    def read_external_control(self):
        # PROTECTED REGION ID(SoftiGalilShutter.external_control_read) ENABLED START #
        """Return the external_control attribute."""
        return self._external_control
        # PROTECTED REGION END #    //  SoftiGalilShutter.external_control_read

    def read_open_value(self):
        # PROTECTED REGION ID(SoftiGalilShutter.open_value_read) ENABLED START #
        """Return the open_value attribute."""
        return self._open_value
        # PROTECTED REGION END #    //  SoftiGalilShutter.open_value_read

    def write_open_value(self, value):
        # PROTECTED REGION ID(SoftiGalilShutter.open_value_write) ENABLED START #
        """Set the open_value attribute."""
        self._open_value = value
        # PROTECTED REGION END #    //  SoftiGalilShutter.open_value_write

    def read_close_value(self):
        # PROTECTED REGION ID(SoftiGalilShutter.close_value_read) ENABLED START #
        """Return the close_value attribute."""
        return self._close_value
        # PROTECTED REGION END #    //  SoftiGalilShutter.close_value_read

    def write_close_value(self, value):
        # PROTECTED REGION ID(SoftiGalilShutter.close_value_write) ENABLED START #
        """Set the close_value attribute."""
        self._close_value = value
        # PROTECTED REGION END #    //  SoftiGalilShutter.close_value_write

    def read_closing_tolerance(self):
        # PROTECTED REGION ID(SoftiGalilShutter.closing_tolerance_read) ENABLED START #
        """Return the closing_tolerance attribute."""
        return self._closing_tolerance
        # PROTECTED REGION END #    //  SoftiGalilShutter.closing_tolerance_read

    def write_closing_tolerance(self, value):
        # PROTECTED REGION ID(SoftiGalilShutter.closing_tolerance_write) ENABLED START #
        """Set the closing_tolerance attribute."""
        self._closing_tolerance = value
        # PROTECTED REGION END #    //  SoftiGalilShutter.closing_tolerance_write

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def TurnOn(self):
        # PROTECTED REGION ID(SoftiGalilShutter.TurnOn) ENABLED START #
        """
        Turn the motor on.

        :return:None
        """
        self._init_motor()
        # PROTECTED REGION END #    //  SoftiGalilShutter.TurnOn

    @command(
    )
    @DebugIt()
    def TurnOff(self):
        # PROTECTED REGION ID(SoftiGalilShutter.TurnOff) ENABLED START #
        """
        Turn the motor off.

        :return:None
        """
        try:
            print('ST A sent, ', self.g.GCommand('ST A'))
            print('MO sent, ', self.g.GCommand('MO'))
            self.set_state(DevState.OFF)
        except gclib.GclibError as e:
            self.g.GClose()
            self.set_state(DevState.FAULT)
            print('Error in TurnOff(): ', e)
        # PROTECTED REGION END #    //  SoftiGalilShutter.TurnOff

    @command(
    )
    @DebugIt()
    def StopMotor(self):
        # PROTECTED REGION ID(SoftiGalilShutter.StopMotor) ENABLED START #
        """
        Stop motor.

        :return:None
        """
        try:
            print('Stopping the motor: ', self.g.GCommand('ST A'))
            self.set_state(DevState.STANDBY)
        except gclib.GclibError as e:
            self.set_state(DevState.FAULT)
            print('Unexpected GclibError:', e)
        # PROTECTED REGION END #    //  SoftiGalilShutter.StopMotor

    @command(
    )
    @DebugIt()
    def FindIndex(self):
        # PROTECTED REGION ID(SoftiGalilShutter.FindIndex) ENABLED START #
        """
        Find the index mark on the encoder.

        :return:None
        """
        try:
            self._stop_all()
            self._external_control = False
            program = '#A;ST;MO A;JG 5000;FI;SH A;BG A;EN' # Find index Galil program
            self.g.GProgramDownload(program, '--max 3')
            #print(' Uploaded program:\n%s' % self.g.GProgramUpload())
            print('FindIndex(): ', self.g.GCommand('XQ'))
            self.set_state(DevState.UNKNOWN)
        except Exception as e:
            self.set_state(DevState.FAULT)
            print('Error in FindIndex():', e)
        # PROTECTED REGION END #    //  SoftiGalilShutter.FindIndex

    def is_FindIndex_allowed(self):
        # PROTECTED REGION ID(SoftiGalilShutter.is_FindIndex_allowed) ENABLED START #
        return self.get_state() not in [DevState.MOVING]
        # PROTECTED REGION END #    //  SoftiGalilShutter.is_FindIndex_allowed

    @command(
    )
    @DebugIt()
    def ExternalControl(self):
        # PROTECTED REGION ID(SoftiGalilShutter.ExternalControl) ENABLED START #
        """
        Switch to hardware control input. Shutter is controlled from one of the digital inputs.

        :return:None
        """
        try:
            # self.t = Thread(target=self._switch_to_ext_ctrl,
            #                         args=(self._close_value, self._open_value))
            # self.t.setDaemon(True)
            # self.t.start()
            self._switch_to_ext_ctrl(self._close_value, self._open_value)
        except Exception as e:
            print(f"Error in the external control switch: {e}")
        # PROTECTED REGION END #    //  SoftiGalilShutter.ExternalControl

    def is_ExternalControl_allowed(self):
        # PROTECTED REGION ID(SoftiGalilShutter.is_ExternalControl_allowed) ENABLED START #
        return self.get_state() not in [DevState.OPEN]
        # PROTECTED REGION END #    //  SoftiGalilShutter.is_ExternalControl_allowed

    @command(
    )
    @DebugIt()
    def GalilSoftReset(self):
        # PROTECTED REGION ID(SoftiGalilShutter.GalilSoftReset) ENABLED START #
        """
        Galil soft reset. Sends `RS` command to the controller.

        :return:None
        """
        try:
            print('Controller reset: ', self.g.GCommand('RS'))
            self.set_state(DevState.STANDBY)
        except Exception as e:
            self.g.GClose()
            self.set_state(DevState.FAULT)
            print('Error in GalilSoftReset: ', e)
        # PROTECTED REGION END #    //  SoftiGalilShutter.GalilSoftReset

    def is_GalilSoftReset_allowed(self):
        # PROTECTED REGION ID(SoftiGalilShutter.is_GalilSoftReset_allowed) ENABLED START #
        return self.get_state() not in [DevState.MOVING]
        # PROTECTED REGION END #    //  SoftiGalilShutter.is_GalilSoftReset_allowed

    @command(
        dtype_in='DevString',
        doc_in="Manual command input.",
        dtype_out='DevBoolean',
        doc_out="Returns True if the command was successful.",
    )
    @DebugIt()
    def SingleCommandInput(self, argin):
        # PROTECTED REGION ID(SoftiGalilShutter.SingleCommandInput) ENABLED START #
        """

        :param argin: 'DevString'
        Manual command input.

        :return:'DevBoolean'
        Returns True if the command was successful.
        """
        try:
            print('Galil manual command input..', argin)
            response = self.g.GCommand(argin)
            print("The response was: ", response)

            self.info_stream(response)
            self.set_state(DevState.UNKNOWN)
            return True
        except Exception as e:
            self.set_state(DevState.FAULT)
            print('Error in SingleCommandInput():', e)
            return False
        # PROTECTED REGION END #    //  SoftiGalilShutter.SingleCommandInput

    @command(
    )
    @DebugIt()
    def Open(self):
        # PROTECTED REGION ID(SoftiGalilShutter.Open) ENABLED START #
        """
        Opens the shutter.

        :return:None
        """
        self._open_shutter()
        # PROTECTED REGION END #    //  SoftiGalilShutter.Open

    def is_Open_allowed(self):
        # PROTECTED REGION ID(SoftiGalilShutter.is_Open_allowed) ENABLED START #
        if self._external_control:
            return False
        return self.get_state() not in [DevState.MOVING]
        # PROTECTED REGION END #    //  SoftiGalilShutter.is_Open_allowed

    @command(
    )
    @DebugIt()
    def Close(self):
        # PROTECTED REGION ID(SoftiGalilShutter.Close) ENABLED START #
        """
        Closes the shutter.

        :return:None
        """
        self._close_shutter()
        # PROTECTED REGION END #    //  SoftiGalilShutter.Close

    def is_Close_allowed(self):
        # PROTECTED REGION ID(SoftiGalilShutter.is_Close_allowed) ENABLED START #
        if self._external_control:
            return False
        return self.get_state() not in [DevState.MOVING]
        # PROTECTED REGION END #    //  SoftiGalilShutter.is_Close_allowed

    @command(
    )
    @DebugIt()
    def SoftCtrl(self):
        # PROTECTED REGION ID(SoftiGalilShutter.SoftCtrl) ENABLED START #
        """
        Switches to software (via Tango) control of the shutter.

        :return:None
        """
        self._init_motor()
        self._close_shutter()
        self._external_control = False
        # PROTECTED REGION END #    //  SoftiGalilShutter.SoftCtrl

    def is_SoftCtrl_allowed(self):
        # PROTECTED REGION ID(SoftiGalilShutter.is_SoftCtrl_allowed) ENABLED START #
        return self.get_state() not in [DevState.OPEN]
        # PROTECTED REGION END #    //  SoftiGalilShutter.is_SoftCtrl_allowed

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the SoftiGalilShutter module."""
    # PROTECTED REGION ID(SoftiGalilShutter.main) ENABLED START #
    return run((SoftiGalilShutter,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SoftiGalilShutter.main


if __name__ == '__main__':
    main()
