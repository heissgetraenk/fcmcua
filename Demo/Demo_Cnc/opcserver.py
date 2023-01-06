from asyncua import Server, ua
from datetime import datetime
import asyncio

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
        s_widths[axis] = (targets[axis] - prev_values[axis])/steps

    # loop, take a step each cycle
    # loop_time = 0.0
    # cyc_start = datetime.now()
    for s in range(0,steps-1):
        print("Step:", s)
        for axis in targets:
            new_value = prev_values[axis] + ((s+1) * s_widths[axis])
            dv = ua.DataValue(ua.Variant(new_value, ua.VariantType.Double))
            await axis.write_value(dv)
        await print_vars(vars)
        await asyncio.sleep(9*TICK/12)

    # cyc_end = datetime.now()
    # loop_time = (cyc_end - cyc_start).total_seconds()
    # print('time per step:',loop_time/(steps-1))

    #make sure to land on the target values
    for axis in targets:
        new_value = targets[axis]
        dv = ua.DataValue(ua.Variant(new_value, ua.VariantType.Double))
        await axis.write_value(dv)
        await print_vars(vars)

    
    after = datetime.now()
    difference = after - before
    time_elapsed = difference.total_seconds()
    print("This g01 schould have taken ", t, "s")
    print('This g01 took:', time_elapsed)



async def toggle_doors(vars):
    print("Toggle doors")
    await vars['Open'].write_value(True if (await vars['Open'].get_value() == False) else False)
    await vars['Close'].write_value(True if (await vars['Close'].get_value() == False) else False)
    await print_vars(vars)


async def close_doors(vars):
    print("Close doors")
    await vars['Open'].write_value(False)
    await vars['Close'].write_value(True)
    await print_vars(vars)


async def open_doors(vars):
    print("Open doors")
    await vars['Open'].write_value(True)
    await vars['Close'].write_value(False)
    await print_vars(vars)


async def print_vars(vars):
    result = ''
    for v in vars:
        value = str(await vars[v].get_value())
        result += (v + ': ' + value + ', ')
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
    vars['Open'] = (await myNode.add_variable(idx, "Open", False))
    vars['Close'] = (await myNode.add_variable(idx, "Close", False))

    # set all variables writable
    for v in vars:
        await vars[v].set_writable()
        print(v, vars[v])


    #start the server
    async with server:
        while True:
            cmd = input('Enter a command:')

            if cmd == 'start':
                await(close_doors(vars))
                await g01({vars['X']:1500, vars['Y']:800}, 1000, vars)
                await(open_doors(vars))

            elif cmd == 'doors':
                await toggle_doors(vars)


if __name__ == "__main__":
    asyncio.run(main())
