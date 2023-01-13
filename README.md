# FreeCAD Motion Control Workbench FCMCUA
Link a motion controller to a FreeCAD assembly using OPC UA. This workbench can be used to manipulate assemblies created by the [Assembly4](https://github.com/Zolko-123/FreeCAD_Assembly4) workbench. It does so by updating the Attachment Offsets of the assembly's Local Coordinate Systems to match the target position values provided by the OPC UA server.

## Use cases:

- **Virtual Commissioning**  
  Visualize PLC motion control code on a mock-up of your target machine before testing it on the real hardware. This is especially useful if the machine is not yet built or even fully designed.
  Many modern PLCs posses OPC UA servers, that can be activated to read data from the controller. Configure the OPC UA server, connect your FreeCAD assembly to your PLC (or its digital twin) and take a look at what your PLC code is doing, even without access to a physical prototype of your target machine.

- **Interactive animations**  
  Write your own minimal OPC UA server with an embedded script for interaction with your Assembly4 Model. An example can be found [here](https://github.com/heissgetraenk/fcmcua/tree/main/Demo/Demo_Cnc).  

![fcmcua_demo](https://user-images.githubusercontent.com/104628764/211853683-031cf2f3-6bcc-41fa-9d38-f4cbf12fcaa7.gif)  

## Installation:  

I am new to writing FreeCAD workbenches and have not been able to figure out how to get Fcmcua installed automatically. So unfortunately installation has to be done manually at this point. Any pointers on how to automate this process are more than welcome.

### Manual Installation:  

This workbench was tested on FreeCAD v0.20.1 and with Python 3.10.5.

#### Linux:  

1. When using a FreeCAD AppImage: make sure you have the same python version installed, as packaged into the AppImage
2. Install dependencies into the correct python version: 
    1. `pip install asyncua`
    2. `pip install pyside2`    
3. Place the files from [freecad.fcmcua/freecad/fcmcua](https://github.com/heissgetraenk/fcmcua/tree/main/freecad.fcmcua/freecad/fcmcua) in your FreeCAD/Mod directory:
    * package install: *~/.FreeCAD/Mod*
    * AppImage: *~/.local/share/FreeCAD/Mod*
    * Make sure to use this directory structure: *~/.FreeCAD/Mod/freecad.fcmcua/freecad/fcmcua*
4. Edit the paths in **fcmcua.ini**:
    1. **PyPath**: Path to your python packages
    2. **WbPath**: Path to where you placed the workbench files

## Usage:  

**Some basics:** Fcmcua works by updating the AttachmentOffsets of the Local Coordinate Systems (LCS) with which the individual parts are attached to one another. Take a look at the command that does this:  

```python
  import FreeCAD as App

  App.getDocument(doc).getObjectsByLabel(fc_obj)[0].AttachmentOffset = App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(v_x, v_y, v_z), angle))
```
As you can see, the FreeCAD part that contains the LCS is given a Placement object. The LCS whose AttachmentOffset is updated is identified by the name of the Part's document and the Label you have given the LCS.  

Note also, that the Placement object given to the LCS contains a position and a rotation. The Fcmcua workbench gets values from an OPC UA node and plugs them into the x, y, z or angle of the Placement object. For Fcmcua to know where each value goes, you need to configure each Node - Placement pairing.  

### Configuring Axis Settings:  

To set the number of axis nodes you want to configure, edit the **fcmcua.ini** file in the Fcmcua install directory.

 ![axis_settings](https://user-images.githubusercontent.com/104628764/212299899-c6022ade-881f-4acd-a94e-dfa800b48d07.png)

* **Node Id:**        Node Id on the OPC UA server. Fcmcua expects a string that looks like this: *ns=2;i=2*  
* **Sign:**           The value coming from the OPC node might be oriented opposite to the direction in which you assembled the model. Invert the value by selecting +/-.  
* **Factor:**         This gets multiplied with the value comming from the node. If for example you control a motor by outputting a speed or rotor-position, you might not have a variable in your controller that represents the actual position of that axis. In that case you might want to factor in a gear ratio to derive the position from the value that you do have in the controller.  
* **Document Name:**  The name of the file containing the Local Coordinate System.  
* **LCS:**            The label you have given the Local Coordinate System (LCS)  
* **Offset:**         The part of the AttachmentOffset that the value from the OPC node will be plugged into. The selected x, y, z or angle correspond to the the vector components in the App.Placement command shown above.  
* **Type:**           What kind of value does the OPC node represent: An axis **pos**ition or a motor **speed**?  

### Configuring Actuator Settings:  

Think of actuators as anything that performs a motion and is started/stopped by binary signals. To set the number of actuator nodes you want to configure, edit the **fcmcua.ini** file in the Fcmcua install directory.

![actuator_settings](https://user-images.githubusercontent.com/104628764/212299969-1e048288-ebc0-4795-88fe-0ba7e67ab762.png) 
![Doorsdemo](https://user-images.githubusercontent.com/104628764/212299978-eeaaea8d-1558-4cc1-a440-5fa7c09a5190.gif)

* **Type:**                      Is the actuator opened and closed by separate signals or is it actuated in one direction and returns automatically when the actuating signal is *False*?  
* **Conditional Block:**         The actuator may be stopped somewhere along its path by another signal (e.g. a sensor detecting a piston position and stopping the piston, or a mechanical block interjecting the pistons travel).  
* **Open/Close/Block Node Ids:** OPC UA Node Id of the binary signal used to open/close/block the actuator.  
* **FreeCAD object:**            Similar to the configuration of the axis settings: *document name*, *LCS label*, *Offset component*  
* **Open/Close/Block Position:** Position the actuator will be opened/closed to or blocked at.  
* **Open/Close Duration:**       The time the actuator should take to open/close.

### Connecting to the OPC UA server  

![connect_panel](https://user-images.githubusercontent.com/104628764/212300030-0c74597d-ebbb-4205-8562-0e1779ae42e7.png)

* **URL:**          Server address in the format opc.tcp://*ip-address*:4840
* **Polling rate:** Time between polls of the OPC values. How low this can be set to is limited by the time it takes to recompute the FreeCAD model after each update. The polling rate also serves to give the actuator logic a reference for how wide to make the steps for each tick. Try to match the polling rate to the compute time for accuracy in that regard.

## A word on Performance

Fcmcua performs a recompute of the assembly model after each update. How fast it manages to do so is mainly dependent on the complexity of your parts and size of your overall model. It is therefore recommended to  build a very rough mockup of the kinematics of the physical machine you intend to program. A faithful CAD rendition of your machine will very likely take too long to recompute to make for a useable animation.  

The system I tested it on (Ryzen 7 3700X, RTX2070, 16GB RAM at 3200MHz) managed about 10-13 updates per second, depending on what else the system was doing at the time. Your mileage may vary.  

If you have thoughts on how to optimize the recompute performance, please let me know.

## ToDo  

This workbench is very much a work in progress. Any advice is welcome, as are contributions to the code. The following points could be improved upon in the future:  

* comments and code clean up (I'll get to it someday, I swear!)
* exception handling and handling of inputs: make sure something userfriendly happens when things go wrong
* automate the installation process  
* change the number of axis/actuators from the Gui  
* accept Node Ids in the form of *ns=2;VariableName*  
* implement a switch metric/imperial or read it from the FreeCAD preferences  
* add +/- option to the actuator config  
* add accelaration to the actuator logic (constant speed at the moment)  
* add button to show/hide whole actuator configuration widget --> might get crowded in models with many actuators  

If you find a bug or have a feature you think would be cool to have in this workbench, open an issue and I'll have a look at it (or at least add it to the ToDo)

## References

* [Assembly4](https://github.com/Zolko-123/FreeCAD_Assembly4) Workbench by [Zolko-123](https://github.com/Zolko-123)
* Tutorial on [FreeCAD Workbenches](https://github.com/felipe-m/tutorial_freecad_wb) by [Felipe Machado](https://github.com/felipe-m)
* Workbench [Starterkit](https://github.com/looooo/Workbench-Starterkit) by [lorenz](https://github.com/looooo)
