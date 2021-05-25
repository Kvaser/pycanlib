
envvar {
  int ev_silent;
}

on start {
  int v;
  v = canGetBusOutputControl();
  envvarSetValue(ev_silent, v==canDRIVER_SILENT);
}

on key 's' {
  int v;
  canSetBusOutputControl(canDRIVER_SILENT);
  v = canGetBusOutputControl();
  envvarSetValue(ev_silent, v==canDRIVER_SILENT);
}

on key 'n' {
  int v;
  canSetBusOutputControl(canDRIVER_NORMAL);
  v = canGetBusOutputControl();
  envvarSetValue(ev_silent, v==canDRIVER_SILENT);
}

on key 'g' {
  int v;
  v = canGetBusOutputControl();
  envvarSetValue(ev_silent, v==canDRIVER_SILENT);
}

on key '?' {

  printf(
  "Envvar:\n"
  "     ev_silent - bool\n"
  "\n"
  "Key events:\n"
  "    'g' - read drivermode and update ev_silent\n"
  "    's' - set drivermode silent, update ev_silent\n"
  "    'n' - set drivermode normal, update ev_silent\n"
  "    '?' - print help text");
}
  