from .. import deprecation
from . import events

memoMsg = deprecation.class_replaced("memoMsg", events.LogEvent)

logMsg = deprecation.class_replaced("logMsg", events.MessageEvent)

rtcMsg = deprecation.class_replaced("rtcMsg", events.RTCEvent)

trigMsg = deprecation.class_replaced("trigMsg", events.TriggerEvent)

verMsg = deprecation.class_replaced("verMsg", events.VersionEvent)
