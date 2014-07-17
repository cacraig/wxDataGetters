import beanstalkc

class Queue:

  def __init__(self):
    # Connect
    self.beanstalk = beanstalkc.Connection(host='192.168.33.10', port=11300)
    self.beanstalk.use('default')
    return

  def insertIntoQueue(self, job):
    self.beanstalk.push(job)
    return

  def reserveJob(self):
    return

  def buryJob():
    return

