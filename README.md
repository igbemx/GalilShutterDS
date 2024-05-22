# GalilShutterDS

Tango device server for controlling a Galil DMC-3x01x motion controller based shutter.

## Functionality

- Connects to a Galil motion controller via its IP address and port.
- Provides attributes for:
    - Device properties (host, port)
    - Shutter position (absolute)
    - Clockwise offset from the index marker
    - External control state (controlled via digital TTL input
    - Adjustable Open and close shutter positions (encoder values)
    - Adjustable closing tolerance (determines open/closed state)
- Offers commands to:
    - Turn the motor on/off
    - Stop motor motion
    - Find the index mark on the encoder
    - Switch to hardware control (external digital inputs)
    - Perform a Galil soft reset
    - Send a single manual command to the Galil controller
    - Open/Close the shutter
    - Switch between software/hardware control via TANGO

