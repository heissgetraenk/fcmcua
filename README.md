# FreeCAD Motion Control Workbench FCMCUA
Link a motion controller to a FreeCAD assembly using OPC UA. This workbench can be used to manipulate assemblies created by the [Assembly4][Asm4] workbench. It does so by updating the Attachment Offsets of the Local Coordinate Systems to match the target position values provided by the OPC UA server.

## Use cases:

- **Virtual Commissioning**
  Visualize PLC motion control code on a mock-up of your target machine before testing it on the real hardware. This is especially useful if the machine is not yet built or even fully designed.
  Many modern PLCs posses OPC UA servers, that can be activated to read data from the controller. Configure the OPC UA server, connect your FreeCAD assembly to your PLC (or its digital twin) and take a look at what your PLC code is doing, even without access to a physical prototype of your target machine.

- **Interactive animations**
  Write your own minimal OPC UA server with an embedded script for interaction with your Assembly4 Model. An example can be found [here][example_opc_server]. 



  ------------------------------------------------------------------------------------------------#
  [Asm4]:https://github.com/Zolko-123/FreeCAD_Assembly4
  [example_opc_server]: https://github.com/heissgetraenk/fcmcua/tree/main/Demo/Demo_Cnc


