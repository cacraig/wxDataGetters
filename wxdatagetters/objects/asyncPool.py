import time
import multiprocessing as mp

class AsyncPool():

  def __init__(self, processes=mp.cpu_count()):
    self.manager = mp.Manager()
    self.nc = self.manager.Value('i', 0)
    self.pids = []
    self.processes = processes
    return

  def doAsync(self, *args):
    nc = args[0]
    method = args[1]
    zargs = args[2:]
    method(zargs)
    nc.value -= 1
    return

  def doJob(self, method, args):
    nArg = (self.nc, method,) + args

    # Wait for some processes to finish before slitting off more processes.
    # Max Number of simultaneous processes = self.processes
    while self.nc.value >= self.processes:
      time.sleep(.1)
    self.nc.value += 1
    p = mp.Process(target=self.doAsync,
                   args=nArg)
    p.start()
    self.pids.append(p)
    return

  def join(self):
    for p in self.pids:
      p.join()