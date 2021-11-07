from usb_dmx.chase_generator import ChaseGenerator
from usb_dmx.dmxctl import DataProducer
from usb_dmx.dataclasses import BPM, Chase
import queue
import cmd
import textwrap


class LightControlCLI(cmd.Cmd):

    # -- Constructor --

    def __init__(self, port: str = 'COM3') -> None:
        cmd.Cmd.__init__(self)
        self.gens = ChaseGenerator()
        self.controller = DataProducer(port, self.gens.gen_blackout())
        self.controller.start()
        self.intro = ('Welcome to light control!\n\n'
                      'Type "help" or "?" to list commands \n')
        self.prompt = '> '

    # -- Text formatting methods --

    def header1(self, title: str, width: int = 72, barchar: str = '=') -> None:
        """Print a header1 to the console"""
        print(f'\n{barchar * 2} {title} '.ljust(width, barchar) + '\n')

    def header2(self, title: str, barchar: str = '-') -> None:
        """Print a header2 to the console"""
        print(f'{barchar * 2} {title} {barchar * 2}\n')

    def paragraph(self,
                  text: str,
                  indent: int = 3,
                  width: int = 72,
                  blankline: bool = True) -> None:
        """Wrap and print a paragraph of text"""
        blank = '\n' if blankline else ''
        print(
            textwrap.fill(text,
                          width,
                          initial_indent=' ' * indent,
                          subsequent_indent=' ' * indent) + blank)

    # -- Error handling methods --

    def unknown_command(self, command: str) -> None:
        print(f'*** Unknown command: {command}\n')

    def error_message(self, e: Exception) -> None:
        print(f'*** ERROR: {e}')

    # -- General commands --

    def put_generator(self, generator: Chase, timeout: float = 0.1) -> None:
        try:
            self.controller.data_queue.put(generator, True, timeout)
        except queue.Full as e:
            self.error_message(e)

    def do_exit(self, arg: str) -> int:
        """Exit the light control program"""
        self.controller.terminated.set()
        self.controller.join()
        return 1

    def do_help(self, arg: str) -> None:
        """List all commands and show their documentation"""
        commands = [
            c.removeprefix('do_') for c in dir(self) if c.startswith('do_')
        ]
        generators = [
            g.removeprefix('gen_') for g in dir(self.gens)
            if g.startswith('gen_')
        ]
        help_pages = [
            h.removeprefix('help_') for h in dir(self) if h.startswith('help_')
        ]
        func = None
        if arg:
            if arg in (commands + generators):
                try:
                    func = getattr(self, f'help_{arg}')
                    return func()
                except AttributeError:
                    print(f'No documentation for command {arg}')
            else:
                self.unknown_command(arg)
        else:
            documented = sorted(
                [h for h in help_pages if h in (commands + generators)])
            undocumented = sorted(
                [c for c in (commands + generators) if c not in help_pages])
            misc = sorted([h for h in help_pages if h not in documented])
            if documented:
                self.header1('Documented commands (type help <command>)')
                self.columnize(documented, 72)
                print('')  # newline
            if undocumented:
                self.header1('Undocumented commands')
                self.columnize(undocumented, 72)
                print('')  # newline
            if misc:
                self.header1('Miscellaneous help topics')
                self.columnize(misc)
                print('')  # newline

    def default(self, line: str) -> bool:
        # For some reason the supeclass definition of this method has
        # type bool. This means this implementation needs to return
        # booleans as well.
        command, *arg = line.split()
        try:
            func = getattr(self.gens, f'gen_{command}')
        except AttributeError:
            try:
                int(line)
                func = self.do_bpm
                arg = [line]
            except ValueError:
                self.unknown_command(command)
                return True
        try:
            self.put_generator(func(*arg))
            return True
        except Exception as e:
            self.error_message(e)
            return True

    def help_exit(self) -> None:
        self.header1('exit')

        # str() is required because __doc__ can be None
        self.paragraph(str(self.do_exit.__doc__))

    def help_help(self) -> None:
        self.header1('help')
        self.paragraph(str(self.do_help.__doc__))
        self.header2('Usage')
        self.paragraph('help')
        self.paragraph('List all available commands.', 6)
        self.paragraph('help <command>')
        self.paragraph('Show documentation of <command>, if available.', 6)

    # -- Custom commands --

    def help_blackout(self) -> None:
        self.header1('blackout')
        self.paragraph(str(self.gens.gen_blackout.__doc__))

    def help_mayday(self) -> None:
        self.header1('mayday')
        self.paragraph(str(self.gens.gen_mayday.__doc__))

    def help_colorwheel(self) -> None:
        self.header1('colorwheel')
        self.paragraph(str(self.gens.gen_colorwheel.__doc__))

    def do_random(self, arg: str) -> None:
        scenes = 5
        if arg:
            try:
                scenes = int(arg)
            except ValueError:
                return print(f'argument is not a number: "{arg}"')
        self.put_generator(self.gens.gen_random(scenes))

    def help_random(self) -> None:
        self.header1('random')
        self.paragraph(str(self.gens.gen_random.__doc__))
        self.header2('Usage')
        self.paragraph('random')
        self.paragraph('Generate a random chase of 5 scenes.', 6)
        self.paragraph('random <scenes>')
        self.paragraph(
            'Generate a random chase of <scenes> scenes.'
            ' <scenes> should be a number.', 6)

    def help_iso(self) -> None:
        color_aliases = ', '.join(self.gens.color_aliases.keys())
        self.header1('iso')
        self.paragraph(str(self.gens.gen_iso.__doc__))
        self.header2('Usage')
        self.paragraph('iso <color>')
        self.paragraph(
            'Switch lamps between <color> and off.'
            ' <color> should be a hexadecimal rgb-value '
            'starting with a "#" (like #ffffff) or'
            ' one of the following values: '
            f'{color_aliases}.', 6)
        self.paragraph('iso <color1> <color2>')
        self.paragraph(
            'Switch lamps between <color1> and <color2>. '
            '<color1> and <color2> should either be '
            'hexadecimals starting with "#" or one of the '
            'values mentioned above.', 6)

    def do_bpm(self, arg: str) -> None:
        """Set the chase speed in beats per minute (BPM)"""
        try:
            self.controller.clock.bpm = BPM(int(arg))
        except ValueError as e:
            self.error_message(e)

    def help_bpm(self) -> None:
        self.header1('bpm')
        self.paragraph(str(self.do_bpm.__doc__))
        self.header2('Usage')
        self.paragraph('<number>', blankline=False)
        self.paragraph('bpm <number>')
        self.paragraph('Set chase speed to <number>.', 6)
