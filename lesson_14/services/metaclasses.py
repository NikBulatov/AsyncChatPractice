from dis import get_instructions


class ServerVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                instructions = get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.opname == "LOAD_GLOBAL":
                        if instruction.argval not in methods:
                            methods.append(instruction.argval)
        if "connect" in methods:
            raise TypeError("Using connect method forbidden in server class")

        if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
            raise TypeError('Invalid socket initialization.')
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(cls, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                instructions = get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    if instruction.opname == "LOAD_GLOBAL":
                        if instruction.argval not in methods:
                            methods.append(instruction.argval)
        for command in ("accept", "listen", "socket"):
            if command in methods:
                raise TypeError("Using forbidden method in class")
        match clsname:
            case "ClientSender":
                if "get_message" in methods and "send_message" not in methods:
                    raise TypeError(
                        "Missing call of function to process with sockets.")
            case "ClientReader":
                if "get_message" not in methods and "send_message" in methods:
                    raise TypeError(
                        "Missing call of function to process with sockets.")
        super().__init__(clsname, bases, clsdict)
