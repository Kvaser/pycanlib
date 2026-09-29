from xml.dom import minidom

from . import kvamemolibxml
from .exceptions import CanlibException

# XML Values
TRIG_LOG_ALL = 'TRIG_LOG_ALL'
TRIG_ON_EVENT = 'TRIG_ON_EVENT'
TRIG_SCRIPTED = 'TRIG_SCRIPTED'


class kvFilter:
    def __init__(self):
        self.msgStop = []
        self.msgPass = []

    def add(self, object):
        if isinstance(object, kvFilterMsgStop):
            self.addMsgStop(object)
        else:
            raise CanlibException(
                f"kvFilter: Can not add object of type {type(object).__name__}!"
            )

    def addMsgStop(self, msgStop):
        self.msgStop.append(msgStop)


class kvFilterMsgStop:
    def __init__(
        self, protocol="NONE", msgid=None, dlc=None, msgid_min=None, channel=0, can_ext="NO"
    ):
        self.msgid = msgid
        if msgid_min is None:
            msgid_min = msgid
        self.msgid_min = msgid_min
        self.dlc = dlc
        self.protocol = protocol
        self.channel = channel
        self.can_ext = can_ext


class kvTrigger:
    def __init__(self, logmode=TRIG_LOG_ALL, fifomode=True):
        self.logmode = logmode
        self.fifomode = fifomode
        self.trigVar = []
        self.statement = []

    def add(self, obj):
        obj.addToTriggerList(self)

    def addStatement(self, trigStatement):
        self.statement.append(trigStatement)

    def getXmlTriggers(self, document):
        xmlTriggers = document.createElement('TRIGGERS')
        for obj in self.trigVar:
            xmlTrigger = obj.getXml(document)
            xmlTriggers.appendChild(xmlTrigger)
        return xmlTriggers

    def getXmlStatements(self, document):
        xmlStatements = document.createElement('STATEMENTS')
        for obj in self.statement:
            xmlStatement = obj.getXml(document)
            xmlStatements.appendChild(xmlStatement)
        return xmlStatements


class kvScript:
    def __init__(self, filename, path=''):
        self.filename = filename
        self.path = path


class kvTrigVarStartup:
    def __init__(self, name="trigger_startup_0"):
        self.name = name

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_STARTUP')
        xmlTrigger.setAttribute('name', self.name)
        return xmlTrigger


class kvTrigVarDiskFull:
    def __init__(self, name="trigger_diskfull_0"):
        self.name = name

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_DISK_FULL')
        xmlTrigger.setAttribute('name', self.name)
        return xmlTrigger


class kvTrigVarTimer:
    def __init__(self, name="trigger_timer_0", offset=600, repeat=False, channel=0, timeout=0):
        self.name = name
        self.offset = offset
        self.repeat = False
        self.channel = channel
        self.timeout = timeout

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_TIMER')
        xmlTrigger.setAttribute('name', self.name)
        xmlTrigger.setAttribute('offset', str(self.offset))
        xmlTrigger.setAttribute('repeat', "YES" if self.repeat else "NO")
        xmlTrigger.setAttribute('timeout', str(self.timeout))
        return xmlTrigger


class kvTrigVarMsgId:
    def __init__(
        self,
        name="trigger_msg_id_0",
        channel=0,
        timeout=0,
        msgid=0,
        msgid_min=None,
        protocol="NONE",
        msg_field=None,
        can_ext="NO",
        can_fd="NO",
    ):
        self.name = name
        self.channel = channel
        self.timeout = timeout
        self.msgid = msgid
        self.msgid_min = msgid_min
        self.protocol = protocol
        self.msg_field = msg_field
        self.can_ext = can_ext
        self.can_fd = can_fd
        if self.msgid_min is None:
            self.msgid_min = self.msgid

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_MSG_ID')
        xmlTrigger.setAttribute('name', self.name)
        xmlTrigger.setAttribute('channel', str(self.channel))
        xmlTrigger.setAttribute('timeout', str(self.timeout))
        xmlTrigger.setAttribute('msgid', str(self.msgid))
        xmlTrigger.setAttribute('msgid_min', str(self.msgid_min))
        xmlTrigger.setAttribute('protocol', str(self.protocol))
        if self.msg_field is not None:
            xmlTrigger.setAttribute('msg_field', str(self.msg_field))
        xmlTrigger.setAttribute('can_ext', str(self.can_ext))
        xmlTrigger.setAttribute('can_fd', str(self.can_fd))
        return xmlTrigger


class kvTrigVarMsgDlc:
    def __init__(
        self, name="trigger_msg_dlc_0", channel=0, timeout=0, dlc=0, dlc_min=None, can_fd="NO"
    ):
        self.name = name
        self.channel = channel
        self.timeout = timeout
        self.dlc = dlc
        self.dlc_min = dlc_min
        self.can_fd = can_fd
        if self.dlc_min is None:
            self.dlc_min = self.dlc

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_MSG_DLC')
        xmlTrigger.setAttribute('name', self.name)
        xmlTrigger.setAttribute('channel', str(self.channel))
        xmlTrigger.setAttribute('timeout', str(self.timeout))
        xmlTrigger.setAttribute('dlc', str(self.dlc))
        xmlTrigger.setAttribute('dlc_min', str(self.dlc_min))
        xmlTrigger.setAttribute('can_fd', str(self.can_fd))
        return xmlTrigger


class kvTrigVarMsgErrorFrame:
    def __init__(self, name="trigger_msg_errorframe_0", channel=0, timeout=0):
        self.name = name
        self.channel = channel
        self.timeout = timeout

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_MSG_ERROR_FRAME')
        xmlTrigger.setAttribute('name', self.name)
        xmlTrigger.setAttribute('channel', str(self.channel))
        xmlTrigger.setAttribute('timeout', str(self.timeout))
        return xmlTrigger


class kvTrigVarSigVal:
    class condition:
        ON_DATA_EQUAL_TO = "ON_DATA_EQUAL_TO"
        ON_DATA_NOT_EQUAL_TO = "ON_DATA_NOT_EQUAL_TO"
        ON_DATA_LARGER_THAN = "ON_DATA_LARGER_THAN"
        ON_DATA_SMALLER_THAN = "ON_DATA_SMALLER_THAN"
        ON_DATA_CHANGE_TO = "ON_DATA_CHANGE_TO"
        ON_DATA_CHANGE_FROM = "ON_DATA_CHANGE_FROM"
        ON_DATA_CHANGE = "ON_DATA_CHANGE"
        ON_DATA_LARGER_THAN_OR_EQUAL = "ON_DATA_LARGER_THAN_OR_EQUAL"
        ON_DATA_SMALLER_THAN_OR_EQUAL = "ON_DATA_SMALLER_THAN_OR_EQUAL"

    class byteorder:
        INTEL = "LITTLE_ENDIAN"
        LITTLE_ENDIAN = "LITTLE_ENDIAN"
        MOTOROLA = "BIG_ENDIAN"
        BIG_ENDIAN = "BIG_ENDIAN"

    def __init__(
        self,
        name="trigger_sigval_0",
        channel=0,
        timeout=0,
        msgid=0,
        dlc=8,
        startbit=0,
        length=8,
        datatype="UNSIGNED",
        byteorder="BIG_ENDIAN",
        protocol="NONE",
        msg_field=None,
        data=0,
        data_min=None,
        condition=condition.ON_DATA_EQUAL_TO,
        can_ext="NO",
        can_fd="NO",
    ):
        self.name = name
        self.channel = channel
        self.timeout = timeout
        self.msgid = msgid
        self.dlc = dlc
        self.startbit = startbit
        self.length = length
        self.datatype = datatype
        self.byteorder = byteorder
        self.data = data
        self.data_min = data_min
        self.protocol = protocol
        self.msg_field = msg_field
        self.can_ext = can_ext
        self.can_fd = can_fd
        self.condition = condition
        if self.data_min is None:
            self.data_min = self.data

    def addToTriggerList(self, triggerList):
        triggerList.trigVar.append(self)

    def getXml(self, document):
        xmlTrigger = document.createElement('TRIGGER_SIGVAL')
        xmlTrigger.setAttribute('name', self.name)
        xmlTrigger.setAttribute('channel', str(self.channel))
        xmlTrigger.setAttribute('timeout', str(self.timeout))
        xmlTrigger.setAttribute('msgid', str(self.msgid))
        xmlTrigger.setAttribute('protocol', str(self.protocol))
        if self.msg_field is not None:
            xmlTrigger.setAttribute('msg_field', str(self.msg_field))
        xmlTrigger.setAttribute('startbit', str(self.startbit))
        xmlTrigger.setAttribute('length', str(self.length))
        xmlTrigger.setAttribute('dlc', str(self.dlc))
        xmlTrigger.setAttribute('datatype', str(self.datatype))
        xmlTrigger.setAttribute('byteorder', str(self.byteorder))
        xmlTrigger.setAttribute('data', str(self.data))
        xmlTrigger.setAttribute('data_min', str(self.data_min))
        xmlTrigger.setAttribute('can_ext', str(self.can_ext))
        xmlTrigger.setAttribute('can_fd', str(self.can_fd))
        xmlTrigger.setAttribute('condition', str(self.condition))
        return xmlTrigger


class kvTrigStatement:
    def __init__(self, expression, preTrigger=0, postTrigger=0):
        self.preTrigger = preTrigger
        self.postTrigger = postTrigger
        self.expression = expression
        self.actions = []

    def add(self, obj):
        if isinstance(obj, kvTrigAction):
            self.actions.append(obj)
        else:
            raise CanlibException(
                f"(kvTrigStatement) Can not add object of type {type(obj).__name__}!"
            )

    def addToTriggerList(self, triggerList):
        triggerList.statement.append(self)

    def getXml(self, document):
        xmlStatement = document.createElement('STATEMENT')
        xmlStatement.setAttribute('pretrigger', str(self.preTrigger))
        xmlStatement.setAttribute('posttrigger', str(self.postTrigger))
        xmlExpression = document.createElement('EXPRESSION')
        text = document.createTextNode(str(self.expression))
        xmlExpression.appendChild(text)
        xmlStatement.appendChild(xmlExpression)
        xmlActions = document.createElement('ACTIONS')
        xmlStatement.appendChild(xmlActions)
        for obj in self.actions:
            xmlAction = obj.getXml(document)
            xmlActions.appendChild(xmlAction)
        return xmlStatement


class kvTrigAction:
    class function:
        START_LOG = 'ACTION_START_LOG'
        STOP_LOG = 'ACTION_STOP_LOG'
        STOP_LOG_COMPLETELY = 'ACTION_STOP_LOG_COMPLETELY'
        ACTIVATE_AUTO_TRANSMIT_LIST = 'ACTION_ACTIVATE_AUTO_TRANSMIT_LIST'
        DEACTIVATE_AUTO_TRANSMIT_LIST = 'ACTION_DEACTIVATE_AUTO_TRANSMIT_LIST'
        EXTERNAL_PULSE = 'ACTION_EXTERNAL_PULSE'

    def __init__(self, function=function.START_LOG, name=None, duration=0):
        self.function = function
        self.name = name
        self.duration = duration

    def getXml(self, document):
        xmlAction = document.createElement(self.function)

        if (
            self.function is kvTrigAction.function.ACTIVATE_AUTO_TRANSMIT_LIST
            or self.function is kvTrigAction.function.DEACTIVATE_AUTO_TRANSMIT_LIST
        ):
            xmlAction.setAttribute('name', str(self.name))

        if self.function is kvTrigAction.function.EXTERNAL_PULSE:
            xmlAction.setAttribute('duration', str(self.duration))

        return xmlAction


class kvMessage:
    def __init__(
        self,
        name,
        msgid,
        data,
        dlc=None,
        can_ext=False,
        can_fd=False,
        can_fd_brs=False,
        error_frame=False,
        remote_frame=False,
    ):
        self.name = name
        self.msgid = msgid
        self.data = data
        self.dlc = dlc
        self.can_ext = can_ext
        self.can_fd = can_fd
        self.can_fd_brs = can_fd_brs
        self.error_frame = error_frame
        self.remote_frame = remote_frame

    def getXml(self, document):
        xmlStatement = document.createElement('MESSAGE')
        xmlStatement.setAttribute('name', self.name)
        xmlStatement.setAttribute('msgid', str(self.msgid))
        data_len = len(self.data)
        if data_len > 8:
            data_len = 8
        if self.dlc is None:
            self.dlc = data_len
        xmlStatement.setAttribute('dlc', str(self.dlc))
        for d in range(0, data_len):
            xmlStatement.setAttribute('b' + str(d), str(self.data[d]))
        xmlStatement.setAttribute('can_ext', "YES" if self.can_ext else "NO")
        xmlStatement.setAttribute('can_fd', "YES" if self.can_fd else "NO")
        xmlStatement.setAttribute('can_fd_brs', "YES" if self.can_fd_brs else "NO")
        xmlStatement.setAttribute('error_frame', "YES" if self.error_frame else "NO")
        xmlStatement.setAttribute('remote_frame', "YES" if self.remote_frame else "NO")
        return xmlStatement


class kvTransmitList:
    def __init__(self, name, msg_delay=0, cycle_delay=0, cyclic=False, autostart=False):
        self.name = name
        self.msg_delay = msg_delay
        self.cycle_delay = cycle_delay
        self.cyclic = cyclic
        self.messages = []

    def add(self, obj):
        if isinstance(obj, kvTransmitMessage):
            self.messages.append(obj)
        else:
            raise CanlibException(
                f"(kvTransmitList) Can not add object of type {type(obj).__name__}!"
            )

    def getXml(self, document):
        xmlTransmitList = document.createElement('TRANSMIT_LIST')
        xmlTransmitList.setAttribute('name', self.name)
        xmlTransmitList.setAttribute('msg_delay', str(self.msg_delay))
        xmlTransmitList.setAttribute('cycle_delay', str(self.cycle_delay))
        xmlTransmitList.setAttribute('cyclic', "YES" if self.cyclic else "NO")
        if self.messages is None:
            return xmlTransmitList
        for message in self.messages:
            xmlTransmitMessage = message.getXml(document)
            xmlTransmitList.appendChild(xmlTransmitMessage)
        return xmlTransmitList


class kvTransmitMessage:
    def __init__(self, name, channel=0):
        self.name = name
        self.channel = channel

    def getXml(self, document):
        xmlTransmitList = document.createElement('TRANSMIT_MESSAGE')
        xmlTransmitList.setAttribute('name', self.name)
        xmlTransmitList.setAttribute('channel', str(self.channel))
        return xmlTransmitList


class ValidationResult:
    def __init__(self, severity, status, text):
        self.severity = severity
        self.status = status
        self.text = text

    def __str__(self):
        return f"[{self.severity} {self.status}]: {self.text}"


class kvMemoConfig:
    def __init__(
        self,
        version="2.0",
        binary_version="6.0",
        afterburner=0,
        log_all=False,
        fifo_mode="NO",
        param_lif=None,
        param_xml=None,
    ):
        if param_lif is not None:
            self.parseLif(param_lif)
        elif param_xml is not None:
            self.parseXml(param_xml)
        else:
            imp = minidom.DOMImplementation()
            doctype = imp.createDocumentType(qualifiedName="KVASER", publicId="", systemId="")
            self.document = imp.createDocument(None, 'KVASER', doctype)
            root = self.document.documentElement
            self.document.appendChild(root)
            comment = self.document.createComment("Created with memoConfig.py")
            root.appendChild(comment)
            child = self.document.createElement('VERSION')
            text = self.document.createTextNode(version)
            child.appendChild(text)
            root.appendChild(child)
            child = self.document.createElement('BINARY_VERSION')
            text = self.document.createTextNode(binary_version)
            child.appendChild(text)
            root.appendChild(child)
            xmlSettings = self.document.createElement('SETTINGS')
            root.appendChild(xmlSettings)
            xmlMode = self.document.createElement('MODE')
            xmlMode.setAttribute('log_all', "YES" if log_all else "NO")
            xmlMode.setAttribute('fifo_mode', fifo_mode)
            xmlSettings.appendChild(xmlMode)
            xmlCanpower = self.document.createElement('CANPOWER')
            xmlCanpower.setAttribute('timeout', str(afterburner))
            xmlSettings.appendChild(xmlCanpower)

    def addBusparams(self, rateParam, channel=0, silent=False, rateParamFd=None, iso=None):
        child = self.document.getElementsByTagName('CAN_BUS')
        if not child:
            child = self.document.createElement('CAN_BUS')
            self.document.documentElement.appendChild(child)
        else:
            child = child[0]
        newchild = self.document.createElement('PARAMETERS')
        newchild.setAttribute('channel', str(channel))
        newchild.setAttribute('bitrate', str(rateParam.freq))
        newchild.setAttribute('tseg1', str(rateParam.tseg1))
        newchild.setAttribute('tseg2', str(rateParam.tseg2))
        newchild.setAttribute('sjw', str(rateParam.sjw))
        newchild.setAttribute('silent', "YES" if silent else "NO")
        if rateParamFd is not None:
            newchild.setAttribute('bitrate_brs', str(rateParamFd.freq))
            newchild.setAttribute('tseg1_brs', str(rateParamFd.tseg1))
            newchild.setAttribute('tseg2_brs', str(rateParamFd.tseg2))
            newchild.setAttribute('sjw_brs', str(rateParamFd.sjw))
            if iso is None:
                iso = True
        if iso is not None:
            newchild.setAttribute('iso', "YES" if iso else "NO")
        child.appendChild(newchild)

    def add(self, obj):
        if isinstance(obj, kvTrigger):
            self.addTrigger(obj)
        elif isinstance(obj, kvFilter):
            self.addFilter(obj)
        elif isinstance(obj, kvMessage):
            self.addMessage(obj)
        elif isinstance(obj, kvTransmitList):
            self.addTransmitList(obj)
        else:
            raise CanlibException(
                f"(kvMemoConfig) Can not add object of type {type(obj).__name__}!"
            )

    def _addFilterAttribute(self, xmlFilterMsg, filter):
        xmlFilterMsg.setAttribute('msgid', str(filter.msgid))
        xmlFilterMsg.setAttribute('msgid_min', str(filter.msgid_min))
        xmlFilterMsg.setAttribute('protocol', str(filter.protocol))
        xmlFilterMsg.setAttribute('can_ext', str(filter.can_ext))
        xmlChannel = self.document.createElement('CHANNEL')
        text = self.document.createTextNode(str(filter.channel))
        xmlChannel.appendChild(text)
        xmlFilterMsg.appendChild(xmlChannel)

    def addFilter(self, filter):
        xmlFilterBlock = self.document.createElement('FILTERS')
        self.document.documentElement.appendChild(xmlFilterBlock)
        if filter is None:
            return

        for obj in filter.msgStop:
            xmlFilterMsg = self.document.createElement('MESSAGE_STOP')
            xmlFilterBlock.appendChild(xmlFilterMsg)
            self._addFilterAttribute(xmlFilterMsg, obj)
        for obj in filter.msgPass:
            xmlFilterMsg = self.document.createElement('MESSAGE_PASS')
            xmlFilterBlock.appendChild(xmlFilterMsg)
            self._addFilterAttribute(xmlFilterMsg, obj)

    def addTrigger(self, trigger):
        xmlTriggerBlock = self.document.createElement('TRIGGERBLOCK')
        self.document.documentElement.appendChild(xmlTriggerBlock)
        if trigger is None:
            return

        xmlTriggers = trigger.getXmlTriggers(self.document)
        xmlTriggerBlock.appendChild(xmlTriggers)

        xmlStatements = trigger.getXmlStatements(self.document)
        xmlTriggerBlock.appendChild(xmlStatements)

    def addMessage(self, message):
        xmlBlocks = self.document.getElementsByTagName('MESSAGES')
        if len(xmlBlocks):
            xmlMessageBlock = xmlBlocks[0]
        else:
            xmlMessageBlock = self.document.createElement('MESSAGES')
            self.document.documentElement.appendChild(xmlMessageBlock)
        if message is None:
            return

        xmlMessage = message.getXml(self.document)
        xmlMessageBlock.appendChild(xmlMessage)

    def addTransmitList(self, transmitList):
        xmlBlocks = self.document.getElementsByTagName('TRANSMIT_LISTS')
        if len(xmlBlocks):
            xmlTranmitListBlock = xmlBlocks[0]
        else:
            xmlTranmitListBlock = self.document.createElement('TRANSMIT_LISTS')
            self.document.documentElement.appendChild(xmlTranmitListBlock)
        if transmitList is None:
            return
        xmlTranmitList = transmitList.getXml(self.document)
        xmlTranmitListBlock.appendChild(xmlTranmitList)

    def addScript(self, script, channel=0):
        xmlScripts = self.document.createElement('SCRIPTS')
        self.document.documentElement.appendChild(xmlScripts)
        xmlScript = self.document.createElement('SCRIPT')
        xmlScript.setAttribute('primary', "YES")
        xmlScript.setAttribute('default_channel', str(channel))
        xmlScripts.appendChild(xmlScript)
        elementScript = self.document.createElement('FILENAME')
        text = self.document.createTextNode(script.filename)
        elementScript.appendChild(text)
        xmlScript.appendChild(elementScript)
        elementPath = self.document.createElement('PATH')
        text = self.document.createTextNode(script.path)
        elementPath.appendChild(text)
        xmlScript.appendChild(elementPath)

    def parseLif(self, conf_lif):
        conf_xml = kvamemolibxml.kvaBufferToXml(conf_lif)
        self.document = minidom.parseString(conf_xml)

    def parseXml(self, conf_xml):
        self.document = minidom.parseString(conf_xml)

    def validate(self):
        result = []
        (countErr, countWarn) = kvamemolibxml.kvaXmlValidate(self.document.toxml())
        while countErr > 0:
            (status, text) = kvamemolibxml.xmlGetValidationError()
            if status == 0:
                break
            result.append(ValidationResult(severity='error', status=status, text=text))
        while countWarn > 0:
            (status, text) = kvamemolibxml.xmlGetValidationWarning()
            if status == 0:
                break
            result.append(ValidationResult(severity='warning', status=status, text=text))
        return result

    def toXml(self):
        return self.document.toxml()

    def toLif(self):
        conf_lif = kvamemolibxml.kvaXmlToBuffer(self.document.toxml())
        return conf_lif


if __name__ == '__main__':
    import canlib

    cl = canlib.canlib()
    rate = cl.translateBaud(freq=canlib.canBITRATE_1M)
    print(rate)

    print("- Manually creating configuration -----------------")
    memoConfig = kvMemoConfig(afterburner=10000)
    memoConfig.addBusparams(channel=0, rateParam=rate)
    memoConfig.addBusparams(channel=1, rateParam=rate)

    trigger = kvTrigger(logmode=TRIG_ON_EVENT, fifomode=False)
    trigVarTimer = kvTrigVarTimer(name="trigger_timer_0", offset=10)
    trigger.add(trigVarTimer)
    trigVarTimer = kvTrigVarTimer(name="trigger_timer_1", offset=20)
    trigger.add(trigVarTimer)
    trigStatement = kvTrigStatement(expression="trigger_timer_0")
    trigger.add(trigStatement)
    trigAction = kvTrigAction(function=kvTrigAction.function.START_LOG)
    trigStatement.add(trigAction)
    trigStatement = kvTrigStatement(expression="trigger_timer_1")
    trigger.add(trigStatement)
    trigAction = kvTrigAction(function=kvTrigAction.function.START_LOG)
    trigStatement.add(trigAction)
    memoConfig.addTrigger(trigger)

    script = kvScript("test_script.txe")
    memoConfig.addScript(script, channel=0)
    outfile = open("firstTry.xml", 'w')
    outfile.write(memoConfig.toXml())
    outfile.close()

    print("- Converting conf.lif to xml -----------------")
    infile = open("conf.lif", 'rb')
    conf_lif = infile.read()
    infile.close()
    memoConfig2 = kvMemoConfig(param_lif=conf_lif)
    outfile = open("conf.xml", 'w')
    outfile.write(memoConfig2.toXml())
    outfile.close()

    print("- Writing manual configuration to firstTry.lif -----------------")
    outfile = open("firstTry.lif", 'wb')
    outfile.write(memoConfig.toLif())
    outfile.close()

    print("- Converting firstTry.lif to xml -----------------")
    infile = open("firstTry.lif", 'rb')
    conf_lif = infile.read()
    infile.close()

    memoConfig2 = kvMemoConfig(param_lif=conf_lif)
    outfile = open("firstTry2.xml", 'w')
    outfile.write(memoConfig2.toXml())
    outfile.close()
