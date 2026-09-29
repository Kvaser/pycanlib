import ctypes as ct
import os
import platform
import struct
import sys
import warnings

from . import futureapi

if sys.platform.startswith("win"):
    # The _winreg module has been renamed to winreg in Python 3.
    try:
        import _winreg as winreg
    except ImportError:
        import winreg as winreg


DEFAULT = object()


def annotate(dll_object, function_name, argtypes, restype=DEFAULT, errcheck=DEFAULT):
    """Fully annotate a dll function using ctypes

    To "annotate" a function is to set its `argtypes`, `restype`, and
    `errcheck` attributes, which should always be done for all used functions.

    This function is used internally by `MyDll`, which only allows access to
    annotated dll functions.

    If `restype` and/or `errcheck` arguments are not specified, the
    `dll_object` argument must have a `default_restype` and/or
    `default_errcheck`, respectively. These values will then be used when
    setting the function's `argtypes` and `restype` attributes.

    """
    function = get_dll_function(dll_object._dll, function_name)
    function.argtypes = argtypes
    # restype and errcheck is optional in the function_prototypes list
    if restype is DEFAULT:
        restype = dll_object.default_restype
    function.restype = restype
    if errcheck is DEFAULT:
        errcheck = dll_object.default_errcheck
    function.errcheck = errcheck
    setattr(dll_object, function_name, function)


def errcheck_by_argp(status_pos, errortype, ok=0):
    """Meta function for generating an error check function

    Returns a newly defined error check function for use with ctypes. This
    error function will inspect the c-function's argument number `status_pos`,
    to find the "status" returned by the operation.

    If this status is equal to `ok` (default 0), the error check function
    signals to ctypes that the call succeeded. Otherwise, the status is passed
    to `errortype` which must return an exception object, which will then be
    raised.

    """

    def errcheck_by_arg(ret, func, args):
        try:
            status_p = args[status_pos]
        except IndexError:
            raise ValueError(
                f"An 'errcheck_by_argp' was created to look at argument no. {status_p}, "
                f"but then used on a function with {len(args)} arguments"
            )

        status = _extract_value_from_pointer(status_p)
        if status == ok:
            return ret
        else:
            raise errortype(status)

    # rename the function based on which position it looks at, to give it some
    # meaning.
    errcheck_by_arg.__name__ += str(status_pos)
    return errcheck_by_arg


def get_dll_function(dll, name):
    try:
        return getattr(dll, name)
    except AttributeError as orig_exc:
        if hasattr(futureapi, name):
            return getattr(futureapi, name)
        else:
            raise orig_exc


class MyDll:
    """Wrapper around a ctypes dll, `MyDll` only allows annotated functions to be called

    The first argument to the `__init__` function, `ct_dll`, is the ctypes dll
    that this object should wrap. It also takes an arbitrary number of keyword
    arguments as "function prototypes". The keyword should match a function in
    the ctypes dll, and the value should be an annotation in the form of
    ``[argtypes, restype, errcheck]``. These values are passed on to
    `dllLoader.annotate`. Note that `restype` and `errcheck` are optional if
    `default_restype` and `default_errcheck` attributes are defined in a
    subclass (respectively).

    After the `MyDll` object has been created, all functions annotated by
    function prototypes are available as attributes, while all other functions
    are not. This effectively forces a function to have been annotated (which
    all functions should be to avoid ctypes defaults) before being used, or an
    `AttributeError` is raised.

    """

    def __init__(self, ct_dll, **function_prototypes):
        self._dll = ct_dll
        for name, prototype in function_prototypes.items():
            annotate(self, name, *prototype)


def no_errcheck(ret, func, args):
    """Dummy error check function that does not do any error checking"""
    return ret


def load_dll(win_name=None, linux_name=None):
    r"""Load dll or shared object file as appropriate.

    On Windows:

        If environment variable 'KVDLLPATH' is set, will try and load DLL named
        win_name from that directory. Otherwise checks registry for CANlib SDK
        installation directory. On 64-bit Windows the registry key is

           HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\KVASER AB\CanlibSDK,

        on 32-bit Windows the registry key is

          `HKEY_LOCAL_MACHINE\SOFTWARE\KVASER AB\CanlibSDK`.

    On Linux:
        If environment variable 'KVDLLPATH' is set, will try and load shared
        object library named linux_name from that directory. Otherwise let
        the OS try and find a matching shared library object.

    """
    # ReadTheDocs does not have canlib dll installed...
    if os.environ.get('READTHEDOCS') == 'True':
        from unittest.mock import MagicMock
        return MagicMock()

    dir = os.getcwd()
    installDir = os.environ.get("KVDLLPATH", "")
    if not installDir:
        if sys.platform.startswith("win"):
            if platform.architecture()[0] == "32bit":
                aKeyName = r"SOFTWARE\KVASER AB\CanlibSDK"
            else:
                aKeyName = r"SOFTWARE\Wow6432Node\KVASER AB\CanlibSDK"
            aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            aKey = winreg.OpenKey(aReg, aKeyName)
            aValue = winreg.QueryValueEx(aKey, "")
            baseDir = str(aValue[0])

            if 8 * struct.calcsize("P") == 32:
                installDir = os.path.join(baseDir, "Bin")
            else:
                installDir = os.path.join(baseDir, "bin_x64")
            installDir = os.path.realpath(installDir)

    if installDir:
        try:
            os.chdir(installDir)
        except FileNotFoundError:
            pass  # Specified directory was not found
        else:
            # Some DLL's are loaded "manually" so we add installDir to the PATH in
            # order to allow the OS to find them later when needed
            os.environ["PATH"] += os.pathsep + installDir

    # Load our dll and all dependencies
    loadedDll = None
    try:
        # Windows supports all dll
        if sys.platform.startswith("win"):
            dllFile = win_name
            if installDir:
                try:
                    # Add installDir to Windows DLL search path
                    _AddDllDirectory = ct.windll.kernel32.AddDllDirectory
                    _AddDllDirectory.argtypes = [ct.c_wchar_p]
                    # Set directory flags to LOAD_LIBRARY_SEARCH_DEFAULT_DIRS
                    ct.windll.kernel32.SetDefaultDllDirectories(0x1000)
                    _AddDllDirectory(installDir)
                except Exception:
                    warnings.warn(
                        "AddDllDirectory only supported on Windows 7 with update "
                        "KB2533623 and newer.",
                        DeprecationWarning,
                    )

            # First we let Windows try and find the dll
            try:
                loadedDll = ct.WinDLL(dllFile)
            except OSError:
                # In Python 3.8, the above started failing, so we now try and
                # load with explicit path. Note that kvrlib may locate
                # and load a canlib32.dll outside of 'installDir'.
                loadedDll = ct.WinDLL(os.path.join(installDir, dllFile))
        elif linux_name is not None:
            dllFile = linux_name
            try:
                # First we try and find the file specified in current directory
                loadedDll = ct.CDLL(os.path.abspath(dllFile))
            except OSError:
                # Then we try and let the system find the shared library
                loadedDll = ct.CDLL(dllFile)
    except Exception as e:
        print(e)
        print(f"Could be a missing dependancy dll for '{dllFile}'.")
        print(f"(Directory for dll: '{installDir}')\n")
        os.chdir(dir)
        exit(1)
    os.chdir(dir)
    return loadedDll


def _extract_value_from_pointer(pointer):
    """Extract the value from any ctypes pointer object"""
    try:
        # pointer constructed with ctypes.byref()
        return pointer._obj.value
    except AttributeError:
        pass

    try:
        # pointer constructed with ctypes.pointer()
        return pointer.contents.value
    except AttributeError:
        pass

    raise ValueError(f"Could not resolve pointer {pointer!r}")
