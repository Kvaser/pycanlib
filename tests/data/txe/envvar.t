
///////////////////////////////////////////////////////////////////////////////////////
//
// This test needs a device with T-script capabilities (PRO)
//
// This program sends a CAN frame with CAN Id 121 - 130
// when any of the 6 Environment Variables below change its value via the canlib API
// (but also then this script starts (we initialize the values) or the environment
//  variable change from within this script upon reception of CAN frame 131 - 140
//  from the testprogram at the PC.
//
/////////////////////////////////////////////////////////////////////////////////////////
variables
{
  const int DATAVAL_SIZE = ENVVAR_MAX_SIZE;  // 4096
  const int DATAVAL2_SIZE = 24;

  int   StartIndex;
  int   Length;
  int   Index;
  char  dataVal[DATAVAL_SIZE];

  int   StartIndex2;
  int   Length2;
  int   Index2;
  char  dataVal2[DATAVAL2_SIZE];
}


envvar
{
  int   IntVal;
  float FloatVal;
  char  DataVal[DATAVAL_SIZE];

  int   IntVal2;
  float FloatVal2;
  char  DataVal2[DATAVAL2_SIZE];
}


on start
{
  // All CAN frames on same channel
  canBusOff();
  canSetBitrate(1000000);
  canSetBusOutputControl(canDRIVER_NORMAL);
  canBusOn();
}

on stop
{
  canBusOff();
}

on envvar IntVal
{
  CanMessage_EnvvarIntPresentValue msg;
  int value;

  envvarGetValue(IntVal, &value);

  printf("IntVal = %d\n", value);

  msg.TheIntValue.Raw = value;

  canWrite(msg);   // CANid 121
}


on envvar FloatVal
{
  CanMessage_EnvvarFloatPresentValue msg;
  float value;

  envvarGetValue(FloatVal, &value);

  printf("FloatVal = %f\n", value);

  msg.TheFloatValue.Raw = value;

  canWrite(msg);    // CANid 122
}


on envvar DataVal
{
  CanMessage_EnvvarDataPresentValueStart msg_start;
  CanMessage_EnvvarDataPresentValueIntermediate msg_middle;
  CanMessage_EnvvarDataPresentValueEnd msg_end;
  char text[DATAVAL_SIZE];
  int totalDataSize;
  int startIndex;
  int remaining;
  int index;

  envvarGetValue(DataVal, text);

  msg_start.StartIndex.Raw = 0;
  startIndex = 0;
  msg_start.Length.Raw = text.count;
  totalDataSize = text.count;
  remaining = totalDataSize;


  //  printf("DataVal = \"%s\", start_index = %d, length = %d",
  //       text[startIndex, totalDataSize], startIndex, totalDataSize);

  printf("Sending start message %d", text.count);
  canWrite(msg_start);    // CANid = 123

  index = 0;
  printf("Sending data (%d messages)", remaining);
  while (remaining > 0)
  {
    // printf("%d, %d, index %d", remaining, remaining / 8, index);
    if ((remaining / 8) > 0) {
      msg_middle.dlc = 8;
      msg_middle.data = text[index + startIndex, 8];
      // printf("%s", msg_middle.data);
      index += 8;
      remaining -= 8;
      int stat = canWrite(msg_middle);    // CANid = 124
      if (stat != 0) {
        printf("WARNING: canWrite failed index:%d, stat:%d\n", index, stat);
      }
    }
    else if (remaining > 0) {
      printf("last middle data %d", remaining);
      msg_middle.dlc = remaining;
      msg_middle.data[0, remaining] = text[index + startIndex, remaining];
      index += remaining;
      remaining -= remaining;
      int stat = canWrite(msg_middle);    // CANid = 124
      if (stat != 0) {
        printf("WARNING: last canWrite failed index:%d, stat:%d\n", index, stat);
      }
    }
  }

  msg_end.dlc = 0;
  canWrite(msg_end);  // CANid = 125
  printf("Sent end message");
}


on envvar IntVal2
{
  CanMessage_EnvvarInt2PresentValue msg;
  int value;

  envvarGetValue(IntVal2, &value);

  printf("IntVal2 = %d\n", value);

  msg.TheIntValue.Raw = value;

  canWrite(0, msg);   // CANid 126
}


on envvar FloatVal2
{
  CanMessage_EnvvarFloat2PresentValue msg;
  float value;

  envvarGetValue(FloatVal2, &value);

  printf("FloatVal2 = %f\n", value);

  msg.TheFloatValue.Raw = value;

  canWrite(0, msg);   // CANid 127
}


on envvar DataVal2
{
  CanMessage_EnvvarData2PresentValueStart msg_start;
  CanMessage_EnvvarData2PresentValueIntermediate msg_middle;
  CanMessage_EnvvarData2PresentValueEnd msg_end;
  char text[DATAVAL2_SIZE];
  int totalDataSize;
  int startIndex;
  int remaining;
  int index;

  envvarGetValue(DataVal2, text);

  msg_start.StartIndex.Raw = 0;
  startIndex = 0;
  msg_start.Length.Raw = text.count;
  totalDataSize = text.count;
  remaining = totalDataSize;

  printf("DataVal2 = \"%s\", start_index = %d, length = %d",
         text[startIndex, totalDataSize], startIndex, totalDataSize);

  canWrite(msg_start);    // CANid = 128

  index = 0;
  while (remaining > 0)
  {
    if ((remaining / 8) > 0) {
      msg_middle.dlc = 8;
      msg_middle.data = text[index + startIndex, 8];
      index += 8;
      remaining -= 8;
      canWrite(msg_middle);    // CANid = 129
    }
    else if (remaining > 0) {
      msg_middle.dlc = remaining;
      msg_middle.data[0, remaining] = text[index + startIndex, remaining];
      index += remaining;
      remaining -= remaining;
      canWrite(msg_middle);    // CANid = 129
    }
  }

  msg_end.dlc = 0;
  canWrite(msg_end);  // CANid = 130
}


on CanMessage EnvvarIntSetValue    // CANid = 131
{
  printf("Setting IntVal = %d\n", this.TheIntValue.Raw);
  envvarSetValue(IntVal, this.TheIntValue.Raw);
}


on CanMessage EnvvarFloatSetValue  // CANid = 132
{
  printf("Setting FloatVal = %f\n", this.TheFloatValue.Raw);
  envvarSetValue(FloatVal, this.TheFloatValue.Raw);
}


on CanMessage EnvvarDataSetValueStart   // CANid = 133
{
  Index = 0;
  StartIndex = this.StartIndex.Raw;
  Length = this.Length.Raw;
  printf("Incoming start:%d, length:%d", StartIndex, Length);
}


on CanMessage EnvvarDataSetValueIntermediate   // CANid = 134
{
   dataVal[Index, this.dlc] = this.data[0, this.dlc];
   Index += this.dlc;
}


on CanMessage EnvvarDataSetValueEnd   // CANid = 135
{
  char text[DATAVAL_SIZE];

  envvarGetValue(DataVal, text);

  text[StartIndex, Length] = dataVal[0, Length];

  /* printf("Setting DataVal \"%s\", start_index = %d, length = %d ==> \"%s\"", */
  /*        dataVal[0, Length], StartIndex, Length, text[0, DATAVAL_SIZE]); */

  envvarSetValue(DataVal, text);
  printf("Incoming DataVal end");
}


on CanMessage EnvvarInt2SetValue    // CANid = 136
{
  printf("Setting IntVal2 = %d\n", this.TheIntValue.Raw);
  envvarSetValue(IntVal2, this.TheIntValue.Raw);
}


on CanMessage EnvvarFloat2SetValue  // CANid = 137
{
  printf("Setting IntFloat2 = %f\n", this.TheFloatValue.Raw);
  envvarSetValue(FloatVal2, this.TheFloatValue.Raw);
}


on CanMessage EnvvarData2SetValueStart   // CANid = 138
{
  Index2 = 0;
  StartIndex2 = this.StartIndex.Raw;
  Length2 = this.Length.Raw;
}


on CanMessage EnvvarData2SetValueIntermediate   // CANid = 139
{
   dataVal2[Index2, this.dlc] = this.data[0, this.dlc];
   Index2 += this.dlc;
}


on CanMessage EnvvarData2SetValueEnd   // CANid = 140
{
  char text[DATAVAL2_SIZE];

  envvarGetValue(DataVal2, text);

  text[StartIndex2, Length2] = dataVal2[0, Length2];

  printf("Setting DataVal2 \"%s\", start_index = %d, length = %d ==> \"%s\"",
         dataVal2[0, Length2], StartIndex2, Length2, text[0, DATAVAL2_SIZE]);

  envvarSetValue(DataVal2, text);
}



