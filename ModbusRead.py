#!/usr/bin/python3
import csv
from pymodbus.client import ModbusSerialClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

# Configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Replace with your serial port
SLAVE_ADDRESS = 1  # Replace with the actual slave address
BAUDRATE = 9600
CSV_FILENAME = 'modbus_data.csv'  # Name of the CSV file

REGISTER_MAP = {
    0x0003: {'name': 'Working Status', 'type': 'bits',
             'bits': ['Hot Water Active', 'Reserved', 'Heating Active', 'Cooling Active',
                      'DC Fan 1 Valid', 'DC Fan 2 Valid', 'Reserved', 'Defrosting Active']},
    0x0004: {'name': 'Output Flags 1', 'type': 'bits',
             'bits': ['compressor', '', '', '', '', 'Fan Motor', 'four-way valve', '']},
    0x0005: {'name': 'Output Flags 2', 'type': 'bits',
             'bits': ['chassis electric heating', '', '', '', '', 'A/C Electric Heating', 'Three-way valve',
                      'Water Tank electric Heating']},
    0x0006: {'name': 'Output Flags 3', 'type': 'bits',
             'bits': ['circulation pump', 'crankshaft electric heating', '', '', '', '', '', '']},
    0x0007: {'name': 'Fault Flag 1', 'type': 'bits',
             'bits': ['Er 14 water tank temperature failure', 'Er 21 ambient temperature failure',
                      'Er 16 external coil temperature failure', '', 'Er27 Leaving water temperature failure',
                      'Er05 high Pressure failure', 'Er06 low Pressure Failure', '']},
    0x0008: {'name': 'Fault Flag 2', 'type': 'bits',
             'bits': ['Er03 water flow failure', '', 'Er32 Leaving Water Temp. Over-heat Protection in Heating Mode',
                      '', '', '', '', '']},
    0x0009: {'name': 'Fault Flag 3', 'type': 'bits',
             'bits': ['', '', '', '', '', '', 'Er18 Discharged gas temperature failure', '']},
    0x000A: {'name': 'Fault Flag 4', 'type': 'bits',
             'bits': ['Er15 Inlet water temperature failure', 'Er12 Discharge gas Over-heat Protection', '', '', '',
                      'Er23 Leaving water Overcooling protection in Cooling Mode', 'Er29 Suction Gas temperature failure',
                      '']},
    0x000B: {'name': 'Fault Flag 5', 'type': 'bits',
             'bits': ['Er69 Low pressure protection', '', 'Er33 High External Coil Temp.',
                      'Er42 Innter Coil Temp. Sensor Failure', '', 'Er72 DC fan Communication failure', '',
                      'Er67 low pressure sensor failure']},
    0x000C: {'name': 'Fault Flag 6', 'type': 'bits',
             'bits': ['', '', 'Er26 radiator temperature failure', 'Er34 inverter module temperature is too high',
                      'Secondary  antifreeze', 'Primary antifreeze', '', '']},
    0x000D: {'name': 'Fault Flag 7', 'type': 'bits',
             'bits': ['', '', '', '', 'Er Inverter module communication failure', 'Er66 DC fan 2 failure',
                      'Er64 DC fan 1 failure', '']},
    0x000E: {'name': 'Inlet water temperature', 'type': 'value', 'multiplier': 0.1, 'unit': '°C'},
    0x000F: {'name': 'Water tank temperature', 'type': 'value', 'multiplier': 0.5, 'unit': '°C'},
    0x0011: {'name': 'Ambient temperature', 'type': 'value', 'multiplier': 0.5, 'unit': '°C'},
    0x0012: {'name': 'Outlet water temperature', 'type': 'value', 'multiplier': 0.5, 'unit': '°C'},
    0x0015: {'name': 'Suction gas temperature', 'type': 'value', 'multiplier': 0.5, 'unit': '°C'},
    0x0016: {'name': 'External coil temperature', 'type': 'value', 'multiplier': 0.5, 'unit': '°C'},
    0x001A: {'name': 'Inner coil temperature', 'type': 'value', 'multiplier': 0.5, 'unit': '°C'},
    0x001B: {'name': 'Exhaust Gas temperature', 'type': 'value', 'multiplier': 1, 'unit': '°C'},
    0x001E: {'name': 'Compressor actual frequency', 'type': 'value', 'unit': 'Hz'},
    0x0023: {'name': 'Compressor current', 'type': 'value', 'unit': 'A'},
    0x0028: {'name': 'Low pressure conversion temperature', 'type': 'value', 'multiplier': 0.1, 'unit': '°C'},
    0x002A: {'name': 'DC water pump speed', 'type': 'value'},
    0x002B: {'name': 'Low pressure value', 'type': 'value', 'multiplier': 0.1, 'unit': 'bar'},
    0x002E: {'name': 'Compressor operating power', 'type': 'value'},
    0x003F: {'name': 'Parameter flag 1', 'type': 'value'},
    0x0040: {'name': 'Control flag 1', 'type': 'value'},
    0x0041: {'name': 'Control flag 2', 'type': 'value'},
    0x0043: {'name': 'Mode', 'type': 'value'},
    0x0044: {'name': 'Defrost frequency', 'type': 'value', 'unit': 'HZ'},
    0x0045: {'name': 'defrost cycle', 'type': 'value', 'unit': 'MIN'},
    0x0046: {'name': 'defrost time', 'type': 'value', 'unit': 'MIN'},
    0x0047: {'name': 'Action cycle of main expansion valve', 'type': 'value', 'unit': 'S'},

    # Add more registers here following the same pattern
}


def read_modbus_registers(client, slave_address, register_addresses):
    """Reads multiple holding registers from a Modbus RTU slave."""
    try:
        # Determine the start and count
        start_address = min(register_addresses)
        end_address = max(register_addresses)
        read_count = end_address - start_address + 1

        # Read the holding registers
        result = client.read_holding_registers(start_address, read_count, slave=slave_address)

        if result.isError():
            print(f"Error reading registers: {result}")
            return None

        # Extract the register values
        registers = result.registers

        # Map the register values to their addresses
        register_values = {}
        for i, register_address in enumerate(sorted(register_addresses)):
            offset = register_address - start_address
            register_values[register_address] = registers[offset]

        return register_values

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
    """Main function to read Modbus data and write it to a CSV file."""
    client = ModbusSerialClient(method='rtu', port=SERIAL_PORT, baudrate=BAUDRATE, parity='N', stopbits=1, bytesize=8, timeout=1)

    if not client.connect():
        print("Failed to connect to Modbus device.")
        return

    try:
        # Get the register addresses from the REGISTER_MAP
        register_addresses = sorted(REGISTER_MAP.keys())

        # Read the registers
        register_values = read_modbus_registers(client, SLAVE_ADDRESS, register_addresses)

        if register_values:
            # Prepare data for CSV writing
            csv_data = []
            header = ['Name', 'Value', 'Unit']
            csv_data.append(header)

            for address in register_addresses:
                reg = REGISTER_MAP[address]
                name = reg['name']
                value = register_values[address]
                unit = ''

                if reg['type'] == 'value':
                    multiplier = reg.get('multiplier', 1)
                    unit = reg.get('unit', '')
                    scaled_value = value * multiplier
                    csv_data.append([name, scaled_value, unit])
                elif reg['type'] == 'bits':
                    bits_str = []
                    for i, bit_name in enumerate(reg['bits']):
                        if bit_name:  # Only print if bit_name is not empty
                            bit_value = (value >> i) & 1
                            bits_str.append(f"{bit_name}: {bool(bit_value)}")

                    csv_data.append([name, ', '.join(bits_str), ''])


            # Write data to CSV file
            with open(CSV_FILENAME, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_data)

            print(f"Modbus data written to {CSV_FILENAME}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
