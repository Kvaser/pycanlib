variables
{
  Timer timer;
  int counter;
}

on start {
  counter = 0;
  timer.timeout = 500; // 500 ms
  timerStart(timer, FOREVER);
}

on Timer timer {
  printf("Text # %d from a t-script\n", counter);

  counter++;
}
