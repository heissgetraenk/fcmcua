from asyncua import Server, ua
from datetime import datetime
import asyncio, aioconsole
import os
import threading as th

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


async def g01(targets, feed, vars):
    '''
    takes a dict with node names as key 
    and target-values as value. 
    feed is the speed with wich the target-values are reached
    '''
    before = datetime.now()
    prev_values = {}
    # current values
    for axis in targets:
        prev_values[axis] = await axis.get_value()
    
    #longest distance
    longest = max(abs(targets[a] - prev_values[a]) for a in targets) #in [mm]
    # time derived from feed [mm/min]
    t =  60*longest/feed #in [s]
    # number of steps based on update rate
    steps = int(t / TICK) #[s]/[s/step]
    print("steps:", steps)

    # step widths
    s_widths = {}
    for axis in targets:
        if steps > 0:
            s_widths[axis] = (targets[axis] - prev_values[axis])/steps
        else:
            s_widths[axis] = 0.0

    # loop, take a step each cycle
    # loop_time = 0.0
    # cyc_start = datetime.now()
    for s in range(0,steps-1):
        for axis in targets:
            new_value = prev_values[axis] + ((s+1) * s_widths[axis])
            dv = ua.DataValue(ua.Variant(new_value, ua.VariantType.Double))
            await axis.write_value(dv)
        await _print_vars(vars)
        await asyncio.sleep(9*TICK/12)

    # cyc_end = datetime.now()
    # loop_time = (cyc_end - cyc_start).total_seconds()
    # print('time per step:',loop_time/(steps-1))

    #make sure to land on the target values
    for axis in targets:
        new_value = targets[axis]
        dv = ua.DataValue(ua.Variant(new_value, ua.VariantType.Double))
        await axis.write_value(dv)
    await _print_vars(vars)

    
    # after = datetime.now()
    # difference = after - before
    # time_elapsed = difference.total_seconds()
    # print("This g01 schould have taken ", t, "s")
    # print('This g01 took:', time_elapsed)



async def toggle_doors(vars):
    print("Toggle doors")
    do_open = await vars['Open'].get_value()
    do_close = await vars['Close'].get_value()
    # toggle doors open if both variables are True
    if do_open and do_close:
        do_close = False
    # toggle doors closed if both variables are False
    elif not do_open and not do_close:
        do_close = True
    # toggle both variables
    else:
        do_open = False if do_open else True
        do_close = False if do_close else True

    await vars['Open'].write_value(do_open)
    await vars['Close'].write_value(do_close)
    await _print_vars(vars)


async def close_doors(vars):
    print("Close doors")
    await vars['Open'].write_value(False)
    await vars['Close'].write_value(True)
    await _print_vars(vars)


async def open_doors(vars):
    print("Open doors")
    await vars['Open'].write_value(True)
    await vars['Close'].write_value(False)
    await _print_vars(vars)


async def _print_vars(vars):
    result = ''
    for v in vars:
        value = str(round((await vars[v].get_value()), 1))
        result += (v + ': ' + value + ', ')
    os.system('clear')
    print(result)

async def main():
    #instantiate the server
    server = Server()
    await server.init()

    #assign the address to the server
    server.set_endpoint(URL)

    #add it to the server
    idx = await server.register_namespace(URI)

    #create a node which will contain the servers variables
    myNode = await server.nodes.objects.add_object(idx, NODE)

    # list of variables
    vars = {}
    test_value = 100.0

    # axis values
    for axis in AXES:
        vars[axis] = await myNode.add_variable(idx, axis, 0.0 + test_value)
        test_value += 10.0

    # door open/close signals
    vars['Open'] = (await myNode.add_variable(idx, "Open", True))
    vars['Close'] = (await myNode.add_variable(idx, "Close", False))

    # set all variables writable
    for v in vars:
        await vars[v].set_writable()
        print(v, vars[v])


    #start the server
    async with server:
        while True:
            os.system('clear')
            cmd = await aioconsole.ainput('Enter a command:')

            if cmd == 'start':
                await(close_doors(vars))
                for i in range(1):
                    await g01({vars['X']:500, vars['Y']:500, vars['Z']:500, vars['A']:0, vars['B']:0}, 5000, vars)
                    await g01({vars['X']:100, vars['Y']:500, vars['Z']:500, vars['A']:180, vars['B']:180}, 5000, vars)
                    await g01({vars['X']:100, vars['Y']:100, vars['Z']:200, vars['A']:0, vars['B']:0}, 5000, vars)
                    await g01({vars['X']:500, vars['Y']:500, vars['Z']:500, vars['A']:180, vars['B']:180}, 5000, vars)
                await(open_doors(vars))

            elif cmd == 'doors':
                await toggle_doors(vars)
            
            elif cmd == 'stop':
                do_open = await vars['Open'].get_value()
                do_close = await vars['Close'].get_value()

                if do_close:
                    await vars['Open'].write_value(False)
                    await vars['Close'].write_value(False)
                elif do_open:
                    await vars['Open'].write_value(True)
                    await vars['Close'].write_value(True)


if __name__ == "__main__":
    asyncio.run(main())
