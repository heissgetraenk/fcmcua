from asyncua import Server, ua
from datetime import datetime
import asyncio, aioconsole
import os

#server address
URL = "opc.tcp://127.0.0.1:4840"

#server namespace
URI = "OPCUA_SIMULATION_SERVER"

#server node name
NODE = "Axes"

# axis configuration
AXES = ['X', 'Y', 'Z', 'A', 'B']

# update rate
TICK = 0.005 #[s/step]

# start values
START_VALS = {'X': 200.0, 'Y': 100.0, 'Z': 500.0 ,'A': 0.0, 'B': 0.0}


async def g01(targets, feed, vars):
    '''
    takes a dict with node names as key 
    and target-values as value. 
    feed is the speed with wich the target-values are reached
    '''
    prev_values = {}
    # current values
    for axis in targets:
        prev_values[axis] = await axis.get_value()

    # calculate step-width for all axes listed in targets, 
    # so that all axes arrive on their target value at the same time
    # this means that all axes take the same amount of steps to reach their targets, 
    # with different step-widths depending on overall distance to the target position
    
    #longest distance between target positions and start positions
    longest = max(abs(targets[a] - prev_values[a]) for a in targets) #in [mm]

    # time [s] to reach furthest target position (derived from feed-value [mm/min])
    t =  60*longest/feed #in [s]

    # number of steps based on update rate and time to target
    steps = int(t / TICK) #[s]/[s/step]

    # step widths for each axis
    s_widths = {}
    for axis in targets:
        if steps > 0:
            s_widths[axis] = (targets[axis] - prev_values[axis])/steps
        else:
            s_widths[axis] = 0.0

    # loop, take a step each cycle
    for s in range(0, steps-1):
        # time at the beginning of the cycle
        cyc_start = datetime.now()

        # calculate new position value per axis
        for axis in targets:
            # increment previous position by one step width
            new_value = prev_values[axis] + ((s+1) * s_widths[axis])
            dv = ua.DataValue(ua.Variant(new_value, ua.VariantType.Double))
            # write value to node variable
            await axis.write_value(dv)

        # print all values to terminal
        await _print_vars(vars)

        # check how long this step has taken
        cyc_end = datetime.now()
        loop_time = (cyc_end - cyc_start).total_seconds()

        # wait for the rest of the tick-interval
        await asyncio.sleep((TICK - loop_time) if loop_time < TICK else 0.0)

    # take one more step to land on the absolute target-value
    # and thereby prevent any math errors from creeping in
    for axis in targets:
        new_value = targets[axis]
        dv = ua.DataValue(ua.Variant(new_value, ua.VariantType.Double))
        # write target value to node variable
        await axis.write_value(dv)
    
    # print all values to terminal
    await _print_vars(vars)


async def toggle_doors(vars):
    # get current state of the door node variables
    do_open = await vars['Open'].get_value()
    do_close = await vars['Close'].get_value()

    # open doors if both variables are True
    if do_open and do_close:
        do_close = False

    # close doors if both variables are False
    elif not do_open and not do_close:
        do_close = True

    # else: flip both variables
    else:
        do_open = False if do_open else True
        do_close = False if do_close else True

    # write values to node variables
    await vars['Open'].write_value(do_open)
    await vars['Close'].write_value(do_close)
    await _print_vars(vars)


async def close_doors(vars):
    # write node variable to close doors
    await vars['Open'].write_value(False)
    await vars['Close'].write_value(True)
    await _print_vars(vars)


async def open_doors(vars):
    # write node variable to open doors
    await vars['Open'].write_value(True)
    await vars['Close'].write_value(False)
    await _print_vars(vars)


async def _print_vars(vars):
    '''
    print given variables to terminal
    '''
    result = ''

    # iterate through list of variables
    for v in vars:
        # get value from node variable, round it to one place
        value = str(round((await vars[v].get_value()), 1))
        # format the string by appending each variable name and its variable value
        result += (v + ': ' + value + ', ')
    # clear the terminal to only display one line
    os.system('clear')
    
    # print the finished string
    print(result)

async def main():
    # initiate the server
    server = Server()
    await server.init()

    # assign the address to the server
    server.set_endpoint(URL)

    # add it to the server
    idx = await server.register_namespace(URI)

    # create a node which will contain the server's variables
    myNode = await server.nodes.objects.add_object(idx, NODE)

    # list of variables
    vars = {}

    # fill variables list
    for axis in AXES:
        vars[axis] = await myNode.add_variable(idx, axis, START_VALS[axis])

    # add door open/close signals to variables list
    vars['Open'] = (await myNode.add_variable(idx, "Open", True))
    vars['Close'] = (await myNode.add_variable(idx, "Close", False))

    # set all variables writable
    for v in vars:
        await vars[v].set_writable()
        # print all variable node ids
        print(v, vars[v])


    #start the server
    async with server:
        first_loop = True
        while True:
            # clear the terminal before asking for a user input
            # first loop: don't clear to keep displaying the node ids
            if not first_loop: os.system('clear')

            # ask for user input
            cmd = await aioconsole.ainput('Enter a command (start, stop, doors):')

            # start: execute example machine program
            if cmd == 'start':
                # example machine program
                # close the doors
                await(close_doors(vars))
                
                # increase loop range run the machine program in repeat
                for i in range(1):
                    # machine program
                    await g01({vars['X']:200, vars['Y']:500, vars['Z']:300, vars['A']:0, vars['B']:45}, 20000, vars)
                    await g01({vars['X']:300, vars['Y']:500, vars['Z']:200, vars['A']:0, vars['B']:45}, 10000, vars)
                    await g01({vars['X']:200, vars['Y']:500, vars['Z']:300, vars['A']:0, vars['B']:45}, 20000, vars)
                    await g01({vars['X']:200, vars['Y']:300, vars['Z']:300, vars['A']:-45, vars['B']:0}, 20000, vars)
                    await g01({vars['X']:200, vars['Y']:300, vars['Z']:280, vars['A']:-45, vars['B']:0}, 20000, vars)
                    await g01({vars['X']:600, vars['Y']:300, vars['Z']:280, vars['A']:-45, vars['B']:0}, 10000, vars)
                    await g01({vars['X']:600, vars['Y']:300, vars['Z']:300, vars['A']:0, vars['B']:45}, 20000, vars)
                    await g01({vars['X']:580, vars['Y']:300, vars['Z']:280, vars['A']:0, vars['B']:45}, 10000, vars)
                    await g01({vars['X']:580, vars['Y']:700, vars['Z']:280, vars['A']:0, vars['B']:45}, 10000, vars)
                    await g01({vars['X']:600, vars['Y']:700, vars['Z']:300, vars['A']:0, vars['B']:45}, 20000, vars)
                    await g01({vars['X']:600, vars['Y']:700, vars['Z']:300, vars['A']:45, vars['B']:0}, 20000, vars)
                    await g01({vars['X']:600, vars['Y']:680, vars['Z']:280, vars['A']:45, vars['B']:0}, 10000, vars)
                    await g01({vars['X']:200, vars['Y']:680, vars['Z']:280, vars['A']:45, vars['B']:0}, 10000, vars)
                    await g01({vars['X']:200, vars['Y']:700, vars['Z']:500, vars['A']:0, vars['B']:0}, 20000, vars)
                    await g01({vars['X']:200, vars['Y']:100, vars['Z']:500, vars['A']:0, vars['B']:0}, 20000, vars)
                
                # open the doors
                await(open_doors(vars))

            # doors: open or close the doors
            elif cmd == 'doors':
                await toggle_doors(vars)
            
            # stop: interrupt the doors command
            elif cmd == 'stop':
                do_open = await vars['Open'].get_value()
                do_close = await vars['Close'].get_value()

                if do_close:
                    await vars['Open'].write_value(False)
                    await vars['Close'].write_value(False)
                elif do_open:
                    await vars['Open'].write_value(True)
                    await vars['Close'].write_value(True)
            
            # end of loop: set the first loop control to False
            first_loop = False


if __name__ == "__main__":
    asyncio.run(main())
