import datetime
import json
import math
import os
import random
import socket
import subprocess
import sys
import time
from typing import Callable

from .evaluator import evaluate_call

from .environment import Environment
from .atoms import Atom, BuiltinFunctionAtom, IntrinsicAtom, ValueAtom

# Helper functions
def addBuiltin(name, func: Callable[[list[Atom]], Atom], env: Environment):
    env.set(name, BuiltinFunctionAtom(name, func))

def expect_args(args: list[Atom], expected: list[int], name: str):
    if len(args) not in expected:
        expected_str = (", ".join(str(e) for e in expected[:-1]) +
                        " or " + str(expected[-1])
                        if len(expected) > 1
                        else expected[0])
        raise Exception(f"Function '{name}' expected {expected_str} arguments but got {len(args)}!")

def init_util(env: Environment):
    """
    Initialize utility functions.
    """
    def _exit(args: list[Atom]) -> Atom:
        expect_args(args, [0, 1], "exit")
        code = args[0].value if len(args) == 1 else 0
        os._exit(code)
    def _assert(args: list[Atom]) -> Atom:
        expect_args(args, [1, 2], "assert")
        if not args[0].value:
            raise Exception(args[1].raw_str())
        return ValueAtom("unit", None)
    addBuiltin("exit", _exit, env)
    addBuiltin("assert", _assert, env)

def init_io(env: Environment):
    """
    Initialize standard IO functions.
    """
    def _print(args: list[Atom]) -> Atom:
        args = map(lambda a: a.raw_str(), args)
        print(*args)
        return ValueAtom("unit", None)
    def _input(args: list[Atom]) -> Atom:
        expect_args(args, [0, 1], "input")
        prompt = args[0].raw_str() if len(args) == 1 else ""
        return ValueAtom("string", input(prompt))
    addBuiltin("print", _print, env)
    addBuiltin("input", _input, env)

def init_sys(env: Environment):
    """
    Initialize system OS functions.
    """
    def _system_run(args: list[Atom]) -> Atom:
        expect_args(args, [1, 2], "system_run")
        cmd = args[0].raw_str()
        shell = args[1].value if len(args) == 2 else True
        subprocess.call(cmd, shell=shell)
        return ValueAtom("unit", None)
    def _system_output(args: list[Atom]) -> Atom:
        expect_args(args, [1, 2], "system_output")
        cmd = args[0].raw_str()
        shell = args[1].value if len(args) == 2 else True
        return ValueAtom("string", subprocess.check_output(cmd, shell=shell).decode("utf-8"))
    def _system_get_envs(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_envs")
        return ValueAtom("map", dict(os.environ))
    def _system_get_env(args: list[Atom]) -> Atom:
        expect_args(args, [1], "system_get_env")
        return ValueAtom("string", os.environ[args[0].raw_str()])
    def _system_set_env(args: list[Atom]) -> Atom:
        expect_args(args, [2], "system_set_env")
        os.environ[args[0].raw_str()] = args[1].raw_str()
        return ValueAtom("unit", None)
    def _system_get_cwd(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_cwd")
        return ValueAtom("string", os.getcwd())
    def _system_set_cwd(args: list[Atom]) -> Atom:
        expect_args(args, [1], "system_set_cwd")
        os.chdir(args[0].raw_str())
        return ValueAtom("unit", None)
    def _system_args(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_args")
        if "--" in sys.argv: return ValueAtom("list", sys.argv[sys.argv.index("--") + 1:])
        return ValueAtom("list", [])
    def _system_pid(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_pid")
        return ValueAtom("number", os.getpid())
    def _system_ppid(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_ppid")
        return ValueAtom("number", os.getppid())
    def _system_platform(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_platform")
        return ValueAtom("string", os.name)
    def _system_username(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_username")
        return ValueAtom("string", os.getlogin())
    def _system_hostname(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_hostname")
        return ValueAtom("string", os.uname().nodename)
    def _system_time_s(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_sec")
        return ValueAtom("number", time.time())
    def _system_time_ms(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_ms")
        return ValueAtom("number", time.time() * 1000)
    def _system_time_us(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_us")
        return ValueAtom("number", time.time() * 1000000)
    def _system_time_ns(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_ns")
        return ValueAtom("number", time.time() * 1000000000)
    def _system_time_min(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_min")
        return ValueAtom("number", time.time() / 60)
    def _system_time_hour(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_hour")
        return ValueAtom("number", time.time() / 3600)
    def _system_time_day(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_day")
        return ValueAtom("number", datetime.datetime.now().day)
    def _system_time_month(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_month")
        return ValueAtom("number", datetime.datetime.now().month)
    def _system_time_week(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_week")
        return ValueAtom("number", datetime.datetime.now().isocalendar()[1])
    def _system_time_year(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_year")
        return ValueAtom("number", datetime.datetime.now().year)
    def _system_time_weekday(args: list[Atom]) -> Atom:
        expect_args(args, [0], "system_get_time_weekday")
        return ValueAtom("number", datetime.datetime.now().weekday())
    def _system_sleep_s(args: list[Atom]) -> Atom:
        expect_args(args, [1], "system_sleep")
        time.sleep(args[0].value)
        return ValueAtom("unit", None)
    def _system_sleep_ms(args: list[Atom]) -> Atom:
        expect_args(args, [1], "system_sleep")
        time.sleep(args[0].value / 1000)
        return ValueAtom("unit", None)
    
    addBuiltin("system_run", _system_run, env)
    addBuiltin("system_output", _system_output, env)
    addBuiltin("system_get_envs", _system_get_envs, env)
    addBuiltin("system_get_env", _system_get_env, env)
    addBuiltin("system_set_env", _system_set_env, env)
    addBuiltin("system_get_cwd", _system_get_cwd, env)
    addBuiltin("system_set_cwd", _system_set_cwd, env)
    addBuiltin("system_args", _system_args, env)
    addBuiltin("system_pid", _system_pid, env)
    addBuiltin("system_ppid", _system_ppid, env)
    addBuiltin("system_platform", _system_platform, env)
    addBuiltin("system_username", _system_username, env)
    addBuiltin("system_hostname", _system_hostname, env)
    addBuiltin("system_time_s", _system_time_s, env)
    addBuiltin("system_time_ms", _system_time_ms, env)
    addBuiltin("system_time_us", _system_time_us, env)
    addBuiltin("system_time_ns", _system_time_ns, env)
    addBuiltin("system_time_min", _system_time_min, env)
    addBuiltin("system_time_hour", _system_time_hour, env)
    addBuiltin("system_time_day", _system_time_day, env)
    addBuiltin("system_time_month", _system_time_month, env)
    addBuiltin("system_time_week", _system_time_week, env)
    addBuiltin("system_time_year", _system_time_year, env)
    addBuiltin("system_time_weekday", _system_time_weekday, env)
    addBuiltin("system_sleep_s", _system_sleep_s, env)
    addBuiltin("system_sleep_ms", _system_sleep_ms, env)

def init_fs(env: Environment):
    """
    Initialize file system functions.
    """
    def _dir_create(args: list[Atom]) -> Atom:
        expect_args(args, [1], "dir_create")
        path = args[0].raw_str()
        os.mkdir(path)
        return ValueAtom("unit", None)
    def _dir_remove(args: list[Atom]) -> Atom:
        expect_args(args, [1], "dir_remove")
        path = args[0].raw_str()
        os.rmdir(path)
        return ValueAtom("unit", None)
    def _dir_exists(args: list[Atom]) -> Atom:
        expect_args(args, [1], "dir_exists")
        path = args[0].raw_str()
        return ValueAtom("bool", os.path.exists(path) and os.path.isdir(path))
    def _dir_files(args: list[Atom]) -> Atom:
        expect_args(args, [1], "dir_files")
        path = args[0].raw_str()
        return ValueAtom("list", os.listdir(path))
    def _file_create(args: list[Atom]) -> Atom:
        expect_args(args, [1], "file_create")
        path = args[0].raw_str()
        open(path, 'w').close()
        return ValueAtom("unit", None)
    def _file_remove(args: list[Atom]) -> Atom:
        expect_args(args, [1], "file_remove")
        path = args[0].raw_str()
        os.remove(path)
        return ValueAtom("unit", None)
    def _file_exists(args: list[Atom]) -> Atom:
        expect_args(args, [1], "file_exists")
        path = args[0].raw_str()
        return ValueAtom("bool", os.path.exists(path) and os.path.isfile(path))
    def _file_read_all(args: list[Atom]) -> Atom:
        expect_args(args, [1], "file_read_all")
        path = args[0].raw_str()
        with open(path, 'r') as f:
            return ValueAtom("string", f.read())
    def _file_read_lines(args: list[Atom]) -> Atom:
        expect_args(args, [1], "file_read_lines")
        path = args[0].raw_str()
        with open(path, 'r') as f:
            return ValueAtom("list", f.readlines())
    def _file_write(args: list[Atom]) -> Atom:
        expect_args(args, [2], "file_write")
        path = args[0].raw_str()
        data = args[1].raw_str()
        with open(path, 'w') as f:
            f.write(data)
            return ValueAtom("unit", None)
    def _file_append(args: list[Atom]) -> Atom:
        expect_args(args, [2], "file_append")
        path = args[0].raw_str()
        data = args[1].raw_str()
        with open(path, 'a') as f:
            f.write(data)
            return ValueAtom("unit", None)
    def _file_size(args: list[Atom]) -> Atom:
        expect_args(args, [1], "file_size")
        path = args[0].raw_str()
        return ValueAtom("number", os.path.getsize(path))
    addBuiltin("dir_create", _dir_create, env)
    addBuiltin("dir_remove", _dir_remove, env)
    addBuiltin("dir_exists", _dir_exists, env)
    addBuiltin("dir_files", _dir_files, env)
    addBuiltin("file_create", _file_create, env)
    addBuiltin("file_remove", _file_remove, env)
    addBuiltin("file_exists", _file_exists, env)
    addBuiltin("file_read_all", _file_read_all, env)
    addBuiltin("file_read_lines", _file_read_lines, env)
    addBuiltin("file_write", _file_write, env)
    addBuiltin("file_append", _file_append, env)
    addBuiltin("file_size", _file_size, env)

def init_net(env: Environment):
    """
    Initialize network functions.
    """
    def _net_ping(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_ping")
        host = args[0].raw_str()
        return ValueAtom("bool", os.system(f"ping -c 1 {host}") == 0)
    def _net_public_ip(args: list[Atom]) -> Atom:
        expect_args(args, [0], "net_get_public_ip")
        return ValueAtom("string", subprocess.check_output("curl -s https://ipinfo.io/ip", shell=True).decode("utf-8").strip())
    def _net_ip_info(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_lookup_ip_info")
        info_json = subprocess.check_output(f"curl -s https://ipinfo.io/{args[0].raw_str()}/json", shell=True).decode("utf-8").strip()
        info_result = json.loads(info_json)
        if isinstance(info_result, dict):
            return ValueAtom("map", info_result)
        return ValueAtom("unit", None)
    # TCP Sockets
    def _net_tcp_socket(args: list[Atom]) -> Atom:
        expect_args(args, [0], "net_tcp_socket")
        return IntrinsicAtom("socket_tcp", socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    def _net_tcp_connect(args: list[Atom]) -> Atom:
        expect_args(args, [3], "net_tcp_connect")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_connect' expected a socket as first argument but got '{args[0].type}'!")
        sock = args[0].value
        host = args[1].raw_str()
        port = args[2].value
        sock.connect((host, port))
        return ValueAtom("unit", None)
    def _net_tcp_send(args: list[Atom]) -> Atom:
        expect_args(args, [2], "net_tcp_send")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_send' expected a socket as first argument but got '{args[0].type}'!")
        sock = args[0].value
        data = args[1]
        if data.type == "string":
            sock.send(data.value.encode("utf-8"))
        elif data.type == "list":
            sock.send(bytes(map(lambda a: a.value, data.value)))
        else:
            raise Exception(f"Function 'net_tcp_send' expected a string or list as second argument but got '{data.type}'!")
        return ValueAtom("unit", None)
    def _net_tcp_recv(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_tcp_recv")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_recv' expected a socket as first argument but got '{args[0].type}'!")
        sock: socket.socket = args[0].value
        size = args[1].value
        data = list(sock.recv(size))
        return ValueAtom("list", list(map(lambda b: ValueAtom("number", b), data)))
    def _net_tcp_recv_all(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_tcp_recv_all")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_recv_all' expected a socket as first argument but got '{args[0].type}'!")
        sock = args[0].value
        size = args[1].value
        data = list(sock.recv(size))
        while len(data) < size:
            data += list(sock.recv(size - len(data)))
        return ValueAtom("list", list(map(lambda b: ValueAtom("number", b), data)))
    def _net_tcp_recv_until(args: list[Atom]) -> Atom:
        expect_args(args, [2], "net_tcp_recv_until")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_recv_until' expected a socket as first argument but got '{args[0].type}'!")
        sock = args[0].value
        delimiter = args[1].raw_str()
        data = list(sock.recv_until(delimiter))
        return ValueAtom("list", list(map(lambda b: ValueAtom("number", b), data)))
    def _net_tcp_recv_line(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_tcp_recv_line")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_recv_line' expected a socket as first argument but got '{args[0].type}'!")
        sock = args[0].value
        data = list(sock.recv_line())
        return ValueAtom("list", list(map(lambda b: ValueAtom("number", b), data)))
    def _net_tcp_close(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_tcp_close")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_close' expected a socket as first argument but got '{args[0].type}'!")
        sock = args[0].value
        sock.close()
        return ValueAtom("unit", None)
    def _net_tcp_bind(args: list[Atom]) -> Atom:
        expect_args(args, [2], "net_tcp_bind")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_accept' expected a socket as first argument but got '{args[0].type}'!")
        sock: socket.socket = args[0].value
        port = args[1].value
        sock.bind((socket.gethostname(), port))
        sock.listen()
        return ValueAtom("unit", None)
    def _net_tcp_accept(args: list[Atom]) -> Atom:
        expect_args(args, [1], "net_tcp_accept")
        if args[0].type != "socket_tcp":
            raise Exception(f"Function 'net_tcp_accept' expected a socket as first argument but got '{args[0].type}'!")
        sock: socket.socket = args[0].value
        client, _ = sock.accept()
        return IntrinsicAtom("socket_tcp", client)
    
    addBuiltin("net_ping", _net_ping, env)
    addBuiltin("net_public_ip", _net_public_ip, env)
    addBuiltin("net_ip_info", _net_ip_info, env)
    addBuiltin("net_tcp_socket", _net_tcp_socket, env)
    addBuiltin("net_tcp_connect", _net_tcp_connect, env)
    addBuiltin("net_tcp_send", _net_tcp_send, env)
    addBuiltin("net_tcp_recv", _net_tcp_recv, env)
    addBuiltin("net_tcp_recv_all", _net_tcp_recv_all, env)
    addBuiltin("net_tcp_recv_until", _net_tcp_recv_until, env)
    addBuiltin("net_tcp_recv_line", _net_tcp_recv_line, env)
    addBuiltin("net_tcp_close", _net_tcp_close, env)
    addBuiltin("net_tcp_bind", _net_tcp_bind, env)
    addBuiltin("net_tcp_accept", _net_tcp_accept, env)

def init_encoding(env: Environment):
    """
    Initialize text encoding functions.
    """
    def _enc_utf8(args: list[Atom]) -> Atom:
        expect_args(args, [1], "enc_utf8")
        if args[0].type != "list":
            raise Exception(f"Function 'enc_utf8' expected a list as first argument but got '{args[0].type}'!")
        if args[0].value.any(lambda a: a.type != "number"):
            raise Exception(f"Function 'enc_utf8' expected a list of numbers as first argument but got a list of '{args[0].value[0].type}'!")
        data = bytes(map(lambda a: a.value, args[0].value))
        return ValueAtom("string", data.decode("utf-8"))
    def _dec_utf8(args: list[Atom]) -> Atom:
        expect_args(args, [1], "dec_utf8")
        if args[0].type != "string":
            raise Exception(f"Function 'dec_utf8' expected a string as first argument but got '{args[0].type}'!")
        data = args[0].value.encode("utf-8")
        return ValueAtom("list", list(map(lambda b: ValueAtom("number", b), data)))
    def _enc_base64(args: list[Atom]) -> Atom:
        expect_args(args, [1], "enc_base64")
        if args[0].type != "list":
            raise Exception(f"Function 'enc_base64' expected a list as first argument but got '{args[0].type}'!")
        if args[0].value.any(lambda a: a.type != "number"):
            raise Exception(f"Function 'enc_base64' expected a list of numbers as first argument but got a list of '{args[0].value[0].type}'!")
        data = bytes(map(lambda a: a.value, args[0].value))
        return ValueAtom("string", data.decode("base64"))
    def _dec_base64(args: list[Atom]) -> Atom:
        expect_args(args, [1], "dec_base64")
        if args[0].type != "string":
            raise Exception(f"Function 'dec_base64' expected a string as first argument but got '{args[0].type}'!")
        data = args[0].value.encode("base64")
        return ValueAtom("list", list(map(lambda b: ValueAtom("number", b), data)))
    addBuiltin("enc_utf8", _enc_utf8, env)
    addBuiltin("dec_utf8", _dec_utf8, env)
    addBuiltin("enc_base64", _enc_base64, env)
    addBuiltin("dec_base64", _dec_base64, env)

def init_conv(env: Environment):
    """
    Initialize conversion functions.
    """
    def _str(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str")
        return ValueAtom("string", args[0].raw_str())
    def _int(args: list[Atom]) -> Atom:
        expect_args(args, [1], "int")
        try:
            return ValueAtom("number", int(args[0].raw_str()))
        except ValueError:
            return ValueAtom("unit", None)
    def _number(args: list[Atom]) -> Atom:
        expect_args(args, [1], "number")
        try:
            return ValueAtom("number", float(args[0].raw_str()))
        except ValueError:
            return ValueAtom("unit", None)
    def _bool(args: list[Atom]) -> Atom:
        expect_args(args, [1], "bool")
        return ValueAtom("bool", args[0].raw_str().lower() == "true")
    def _list(args: list[Atom]) -> Atom:
        expect_args(args, [1], "list")
        if args[0].type == "list":
            return args[0]
        elif args[0].type == "tuple":
            return ValueAtom("list", args[0].value)
        elif args[0].type == "map":
            return ValueAtom("list", list(args[0].pairs.values()))
        elif args[0].type == "string":
            return ValueAtom("list", list(args[0].value))
        return ValueAtom("unit", None)
    def _tuple(args: list[Atom]) -> Atom:
        expect_args(args, [1], "tuple")
        if args[0].type == "list":
            return ValueAtom("tuple", args[0].value)
        elif args[0].type == "tuple":
            return args[0]
        return ValueAtom("unit", None)
    def _map(args: list[Atom]) -> Atom:
        expect_args(args, [1], "map")
        if args[0].type == "map":
            return args[0]
        elif args[0].type == "list":
            # If it is a list of tuples, convert it to a map
            if all(e.type == "tuple" for e in args[0].value):
                return ValueAtom("map", dict(map(lambda t: (t.value[0], t.value[1]), args[0].value)))
            # If it is a list of values, convert it to a map with indices as keys
            return ValueAtom("map", dict(map(lambda t: (ValueAtom("number", t[0]), t[1]), enumerate(args[0].value))))
        elif args[0].type == "string":
            # Try to parse the string as JSON
            try:
                result = json.loads(args[0].value)
                if isinstance(result, dict):
                    return ValueAtom("map", result)
            except json.JSONDecodeError:
                pass
        return ValueAtom("unit", None)
    addBuiltin("str", _str, env)
    addBuiltin("int", _int, env)
    addBuiltin("number", _number, env)
    addBuiltin("bool", _bool, env)
    addBuiltin("list", _list, env)
    addBuiltin("tuple", _tuple, env)
    addBuiltin("map", _map, env)

def init_math(env: Environment):
    """
    Initialize math functions.
    """
    def _range(args: list[Atom]) -> Atom:
        expect_args(args, [1, 2, 3], "range")
        if len(args) == 1:
            return ValueAtom("list", list(range(args[0].value)))
        elif len(args) == 2:
            return ValueAtom("list", list(range(args[0].value, args[1].value)))
        elif len(args) == 3:
            return ValueAtom("list", list(range(args[0].value, args[1].value, args[2].value)))
        return ValueAtom("unit", None)
    def _abs(args: list[Atom]) -> Atom:
        expect_args(args, [1], "abs")
        return ValueAtom("number", abs(args[0].value))
    def _ceil(args: list[Atom]) -> Atom:
        expect_args(args, [1], "ceil")
        return ValueAtom("number", math.ceil(args[0].value))
    def _floor(args: list[Atom]) -> Atom:
        expect_args(args, [1], "floor")
        return ValueAtom("number", math.floor(args[0].value))
    def _round(args: list[Atom]) -> Atom:
        expect_args(args, [1], "round")
        return ValueAtom("number", round(args[0].value))
    def _min(args: list[Atom]) -> Atom:
        expect_args(args, [2], "min")
        return ValueAtom("number", min(args[0].value, args[1].value))
    def _max(args: list[Atom]) -> Atom:
        expect_args(args, [2], "max")
        return ValueAtom("number", max(args[0].value, args[1].value))
    def _sqrt(args: list[Atom]) -> Atom:
        expect_args(args, [1], "sqrt")
        return ValueAtom("number", math.sqrt(args[0].value))
    def _pow(args: list[Atom]) -> Atom:
        expect_args(args, [2], "pow")
        return ValueAtom("number", math.pow(args[0].value, args[1].value))
    def _sin(args: list[Atom]) -> Atom:
        expect_args(args, [1], "sin")
        return ValueAtom("number", math.sin(args[0].value))
    def _cos(args: list[Atom]) -> Atom:
        expect_args(args, [1], "cos")
        return ValueAtom("number", math.cos(args[0].value))
    def _tan(args: list[Atom]) -> Atom:
        expect_args(args, [1], "tan")
        return ValueAtom("number", math.tan(args[0].value))
    def _asin(args: list[Atom]) -> Atom:
        expect_args(args, [1], "asin")
        return ValueAtom("number", math.asin(args[0].value))
    def _acos(args: list[Atom]) -> Atom:
        expect_args(args, [1], "acos")
        return ValueAtom("number", math.acos(args[0].value))
    def _atan(args: list[Atom]) -> Atom:
        expect_args(args, [1], "atan")
        return ValueAtom("number", math.atan(args[0].value))
    def _atan2(args: list[Atom]) -> Atom:
        expect_args(args, [2], "atan2")
        return ValueAtom("number", math.atan2(args[0].value, args[1].value))
    def _log(args: list[Atom]) -> Atom:
        expect_args(args, [1], "log")
        return ValueAtom("number", math.log(args[0].value))
    def _log2(args: list[Atom]) -> Atom:
        expect_args(args, [1], "log2")
        return ValueAtom("number", math.log2(args[0].value))
    def _log10(args: list[Atom]) -> Atom:
        expect_args(args, [1], "log10")
        return ValueAtom("number", math.log10(args[0].value))
    def _exp(args: list[Atom]) -> Atom:
        expect_args(args, [1], "exp")
        return ValueAtom("number", math.exp(args[0].value))
    def _exp2(args: list[Atom]) -> Atom:
        expect_args(args, [1], "exp2")
        return ValueAtom("number", math.exp2(args[0].value))
    def _exp10(args: list[Atom]) -> Atom:
        expect_args(args, [1], "exp10")
        return ValueAtom("number", math.pow(10, args[0].value))
    def _expn(args: list[Atom]) -> Atom:
        expect_args(args, [2], "expn")
        return ValueAtom("number", math.pow(args[0].value, args[1].value))
    def _deg2rad(args: list[Atom]) -> Atom:
        expect_args(args, [1], "rad")
        return ValueAtom("number", math.radians(args[0].value))
    def _rad2deg(args: list[Atom]) -> Atom:
        expect_args(args, [1], "deg")
        return ValueAtom("number", math.degrees(args[0].value))
    def _hypot(args: list[Atom]) -> Atom:
        expect_args(args, [2], "hypot")
        return ValueAtom("number", math.hypot(args[0].value, args[1].value))
    def _gcd(args: list[Atom]) -> Atom:
        expect_args(args, [2], "gcd")
        return ValueAtom("number", math.gcd(args[0].value, args[1].value))
    def _lcm(args: list[Atom]) -> Atom:
        expect_args(args, [2], "lcm")
        return ValueAtom("number", math.lcm(args[0].value, args[1].value))
    def _factorial(args: list[Atom]) -> Atom:
        expect_args(args, [1], "factorial")
        return ValueAtom("number", math.factorial(args[0].value))
    def _is_nan(args: list[Atom]) -> Atom:
        expect_args(args, [1], "is_nan")
        if args[0].type == "number":
            return ValueAtom("bool", math.isnan(args[0].value))
        return ValueAtom("bool", False)
    def _is_inf(args: list[Atom]) -> Atom:
        expect_args(args, [1], "is_inf")
        if args[0].type == "number":
            return ValueAtom("bool", math.isinf(args[0].value))
        return ValueAtom("bool", False)
    def _is_finite(args: list[Atom]) -> Atom:
        expect_args(args, [1], "is_finite")
        if args[0].type == "number":
            return ValueAtom("bool", math.isfinite(args[0].value))
        return ValueAtom("bool", False)
    def _is_integer(args: list[Atom]) -> Atom:
        expect_args(args, [1], "is_integer")
        if args[0].type == "number":
            return ValueAtom("bool", args[0].value.is_integer())
        return ValueAtom("bool", False)
    addBuiltin("range", _range, env)
    addBuiltin("abs", _abs, env)
    addBuiltin("ceil", _ceil, env)
    addBuiltin("floor", _floor, env)
    addBuiltin("round", _round, env)
    addBuiltin("min", _min, env)
    addBuiltin("max", _max, env)
    addBuiltin("sqrt", _sqrt, env)
    addBuiltin("pow", _pow, env)
    addBuiltin("sin", _sin, env)
    addBuiltin("cos", _cos, env)
    addBuiltin("tan", _tan, env)
    addBuiltin("asin", _asin, env)
    addBuiltin("acos", _acos, env)
    addBuiltin("atan", _atan, env)
    addBuiltin("atan2", _atan2, env)
    addBuiltin("log", _log, env)
    addBuiltin("log2", _log2, env)
    addBuiltin("log10", _log10, env)
    addBuiltin("exp", _exp, env)
    addBuiltin("exp2", _exp2, env)
    addBuiltin("exp10", _exp10, env)
    addBuiltin("expn", _expn, env)
    addBuiltin("deg2rad", _deg2rad, env)
    addBuiltin("rad2deg", _rad2deg, env)
    addBuiltin("hypot", _hypot, env)
    addBuiltin("gcd", _gcd, env)
    addBuiltin("lcm", _lcm, env)
    addBuiltin("factorial", _factorial, env)
    addBuiltin("is_nan", _is_nan, env)
    addBuiltin("is_inf", _is_inf, env)
    addBuiltin("is_finite", _is_finite, env)
    addBuiltin("is_integer", _is_integer, env)

def init_random(env: Environment):
    def _random(args: list[Atom]) -> Atom:
        expect_args(args, [0], "random")
        return ValueAtom("number", random.random())
    def _random_int(args: list[Atom]) -> Atom:
        expect_args(args, [2], "random_int")
        return ValueAtom("number", random.randint(args[0].value, args[1].value))
    def _random_range(args: list[Atom]) -> Atom:
        expect_args(args, [2], "random_range")
        return ValueAtom("number", random.randint(args[0].value, args[1].value))
    def _random_choice(args: list[Atom]) -> Atom:
        expect_args(args, [1], "random_choice")
        return random.choice(args[0].value)
    def _random_shuffle(args: list[Atom]) -> Atom:
        expect_args(args, [1], "random_shuffle")
        random.shuffle(args[0].value)
        return ValueAtom("unit", None)
    def _random_seed(args: list[Atom]) -> Atom:
        expect_args(args, [1], "random_seed")
        random.seed(args[0].value)
        return ValueAtom("unit", None)
    addBuiltin("random", _random, env)
    addBuiltin("random_int", _random_int, env)
    addBuiltin("random_range", _random_range, env)
    addBuiltin("random_choice", _random_choice, env)
    addBuiltin("random_shuffle", _random_shuffle, env)
    addBuiltin("random_seed", _random_seed, env)

def init_type(env: Environment):
    """
    Initialize type functions.
    """
    def _typeof(args: list[Atom]) -> Atom:
        expect_args(args, [1], "typeof")
        return ValueAtom("string", args[0].type)
    def _is_type(args: list[Atom]) -> Atom:
        expect_args(args, [2], "is_type")
        return ValueAtom("bool", args[0].type == args[1].raw_str())
    addBuiltin("typeof", _typeof, env)
    addBuiltin("is_type", _is_type, env)

def init_str(env: Environment):
    """
    Initialize string operations.
    """
    def _str_trim(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str_trim")
        return ValueAtom("string", args[0].raw_str().strip())
    def _str_trim_start(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str_trim_start")
        return ValueAtom("string", args[0].raw_str().lstrip())
    def _str_trim_end(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str_trim_end")
        return ValueAtom("string", args[0].raw_str().rstrip())
    def _str_split(args: list[Atom]) -> Atom:
        expect_args(args, [2], "str_split")
        return ValueAtom("list", list(map(lambda s: ValueAtom("string", s), args[0].raw_str().split(args[1].raw_str()))))
    def _str_chars(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str_chars")
        return ValueAtom("list", list(map(lambda c: ValueAtom("string", c), args[0].raw_str())))
    def _str_upper(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str_upper")
        return ValueAtom("string", args[0].raw_str().upper())
    def _str_lower(args: list[Atom]) -> Atom:
        expect_args(args, [1], "str_lower")
        return ValueAtom("string", args[0].raw_str().lower())
    def _str_starts_with(args: list[Atom]) -> Atom:
        expect_args(args, [2], "str_starts_with")
        return ValueAtom("bool", args[0].raw_str().startswith(args[1].raw_str()))
    def _str_ends_with(args: list[Atom]) -> Atom:
        expect_args(args, [2], "str_ends_with")
        return ValueAtom("bool", args[0].raw_str().endswith(args[1].raw_str()))
    def _str_contains(args: list[Atom]) -> Atom:
        expect_args(args, [2], "str_contains")
        return ValueAtom("bool", args[1].raw_str() in args[0].raw_str())
    def _str_index_of(args: list[Atom]) -> Atom:
        expect_args(args, [2], "str_index_of")
        return ValueAtom("number", args[0].raw_str().index(args[1].raw_str()))
    def _str_last_index_of(args: list[Atom]) -> Atom:
        expect_args(args, [2], "str_last_index_of")
        return ValueAtom("number", args[0].raw_str().rindex(args[1].raw_str()))
    def _str_replace(args: list[Atom]) -> Atom:
        expect_args(args, [3], "str_replace")
        return ValueAtom("string", args[0].raw_str().replace(args[1].raw_str(), args[2].raw_str()))

    addBuiltin("str_trim", _str_trim, env)
    addBuiltin("str_trim_start", _str_trim_start, env)
    addBuiltin("str_trim_end", _str_trim_end, env)
    addBuiltin("str_split", _str_split, env)
    addBuiltin("str_chars", _str_chars, env)
    addBuiltin("str_upper", _str_upper, env)
    addBuiltin("str_lower", _str_lower, env)
    addBuiltin("str_starts_with", _str_starts_with, env)
    addBuiltin("str_ends_with", _str_ends_with, env)
    addBuiltin("str_contains", _str_contains, env)
    addBuiltin("str_index_of", _str_index_of, env)
    addBuiltin("str_last_index_of", _str_last_index_of, env)
    addBuiltin("str_replace", _str_replace, env)

def init_list(env: Environment):
    """
    Initialize list operations.
    """
    def _list_append(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_append")
        args[0].value.append(args[1])
        return ValueAtom("unit", None)
    def _list_insert(args: list[Atom]) -> Atom:
        expect_args(args, [3], "list_insert")
        args[0].value.insert(args[1].value, args[2])
        return ValueAtom("unit", None)
    def _list_remove(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_remove")
        args[0].value.remove(args[1])
        return ValueAtom("unit", None)
    def _list_pop(args: list[Atom]) -> Atom:
        expect_args(args, [1], "list_pop")
        return args[0].value.pop()
    def _list_size(args: list[Atom]) -> Atom:
        expect_args(args, [1], "list_size")
        return ValueAtom("number", len(args[0].value))
    def _list_contains(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_contains")
        return ValueAtom("bool", args[1] in args[0].value)
    def _list_index_of(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_index_of")
        return ValueAtom("number", args[0].value.index(args[1]))
    def _list_reverse(args: list[Atom]) -> Atom:
        expect_args(args, [1], "list_reverse")
        args[0].value.reverse()
        return ValueAtom("unit", None)
    def _list_split_at(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_split_at")
        return ValueAtom("tuple", (args[0].value[:args[1].value], args[0].value[args[1].value:]))
    def _list_find(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_find")
        return ValueAtom("number", args[0].value.index(args[1]))
    def _list_find_last(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_find_last")
        return ValueAtom("number", args[0].value[::-1].index(args[1]))
    def _list_find_all(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_find_all")
        return ValueAtom("list", list(filter(lambda e: e == args[1], args[0].value)))
    def _list_map(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_map")
        return ValueAtom("list", list(map(lambda e: evaluate_call(args[1], [e]), args[0].value)))
    def _list_filter(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_filter")
        return ValueAtom("list", list(filter(lambda e: evaluate_call(args[1], [e]).value, args[0].value)))
    def _list_reduce(args: list[Atom]) -> Atom:
        expect_args(args, [2, 3], "list_reduce")
        if len(args) == 2:
            acc = args[0].value[0]
            for e in args[0].value[1:]: acc = evaluate_call(args[1], [acc, e])
            return acc
        else: # len(args) == 3
            acc = args[2]
            for e in args[0].value: acc = evaluate_call(args[1], [acc, e])
            return acc
    def _list_group_by(args: list[Atom]) -> Atom:
        expect_args(args, [2], "list_group_by")
        groups = {}
        for e in args[0].value:
            key = evaluate_call(args[1], [e]).raw_str()
            if key not in groups:
                groups[key] = ValueAtom("list", [])
            groups[key].value.append(e)
        return ValueAtom("map", groups)

    addBuiltin("list_append", _list_append, env)
    addBuiltin("list_insert", _list_insert, env)
    addBuiltin("list_remove", _list_remove, env)
    addBuiltin("list_pop", _list_pop, env)
    addBuiltin("list_size", _list_size, env)
    addBuiltin("list_contains", _list_contains, env)
    addBuiltin("list_index_of", _list_index_of, env)
    addBuiltin("list_reverse", _list_reverse, env)
    addBuiltin("list_split_at", _list_split_at, env)
    addBuiltin("list_find", _list_find, env)
    addBuiltin("list_find_last", _list_find_last, env)
    addBuiltin("list_find_all", _list_find_all, env)
    addBuiltin("list_map", _list_map, env)
    addBuiltin("list_filter", _list_filter, env)
    addBuiltin("list_reduce", _list_reduce, env)
    addBuiltin("list_group_by", _list_group_by, env)

def init_tuple(env: Environment):
    """
    Initialize tuple operations.
    """
    def _tuple_size(args: list[Atom]) -> Atom:
        expect_args(args, [1], "tuple_size")
        return ValueAtom("number", len(args[0].value))
    def _tuple_contains(args: list[Atom]) -> Atom:
        expect_args(args, [2], "tuple_contains")
        return ValueAtom("bool", args[1] in args[0].value)
    def _tuple_slice(args: list[Atom]) -> Atom:
        expect_args(args, [3], "tuple_slice")
        return ValueAtom("tuple", args[0].value[args[1].value:args[2].value])
    addBuiltin("tuple_size", _tuple_size, env)
    addBuiltin("tuple_contains", _tuple_contains, env)
    addBuiltin("tuple_slice", _tuple_slice, env)

def init_map(env: Environment):
    """
    Initialize map operations.
    """
    def _map_size(args: list[Atom]) -> Atom:
        expect_args(args, [1], "map_size")
        return ValueAtom("number", len(args[0].value))
    def _map_contains(args: list[Atom]) -> Atom:
        expect_args(args, [2], "map_contains")
        for key in args[0].value.keys():
            if key == args[1].raw_str():
                return ValueAtom("bool", True)
        return ValueAtom("bool", False)
    def _map_keys(args: list[Atom]) -> Atom:
        expect_args(args, [1], "map_keys")
        return ValueAtom("list", list(args[0].value.keys()))
    def _map_values(args: list[Atom]) -> Atom:
        expect_args(args, [1], "map_values")
        return ValueAtom("list", list(args[0].value.values()))
    def _map_items(args: list[Atom]) -> Atom:
        expect_args(args, [1], "map_items")
        tuple_pairs = []
        for key, value in args[0].value.items():
            tuple_pairs.append(ValueAtom("tuple", (key, value)))
        return ValueAtom("list", tuple_pairs)
    def _map_remove(args: list[Atom]) -> Atom:
        expect_args(args, [2], "map_remove")
        del args[0].value[args[1]]
        return ValueAtom("unit", None)
    addBuiltin("map_size", _map_size, env)
    addBuiltin("map_contains", _map_contains, env)
    addBuiltin("map_keys", _map_keys, env)
    addBuiltin("map_values", _map_values, env)
    addBuiltin("map_items", _map_items, env)
    addBuiltin("map_remove", _map_remove, env)

def init_stdlib(env: Environment):
    """
    Initialize the standard library.
    """
    init_util(env)
    init_io(env)
    init_sys(env)
    init_fs(env)
    init_net(env)
    init_encoding(env)
    init_conv(env)
    init_math(env)
    init_random(env)
    init_type(env)
    init_str(env)
    init_list(env)
    init_tuple(env)
    init_map(env)
