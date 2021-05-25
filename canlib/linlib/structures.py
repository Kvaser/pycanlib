import ctypes as ct


class MessageInfo(ct.Structure):
    _fields_ = [
        ("timestamp", ct.c_ulong),
        ("synchBreakLength", ct.c_ulong),
        ("frameLength", ct.c_ulong),
        ("bitrate", ct.c_ulong),
        ("checkSum", ct.c_ubyte),
        ("idPar", ct.c_ubyte),
        ("z", ct.c_ushort),  # Dummy for alignment
        ("synchEdgeTime", ct.c_ulong * 4),
        ("byteTime", ct.c_ulong * 8),
    ]
