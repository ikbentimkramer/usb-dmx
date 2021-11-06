from usb_dmx.cli import LightControlCLI
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.prog = 'usb_dmx'
    parser.add_argument('port', type=str, help='Serial port to connect to')
    args = parser.parse_args()
    LightControlCLI(args.port).cmdloop()
