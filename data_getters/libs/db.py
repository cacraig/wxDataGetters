import psycopg2

class NgwipsDB:

  def __init__(self, dbConnStr):
    self.conn = psycopg2.connect(dbConnStr)
    self.cursor = self.conn.cursor()
    return

  def isNewRun(self, model, currentRun):
    currentDbRun = self.getCurrentRun(model)
    # If it is a new run... return True.
    if int(currentDbRun) < int(currentRun):
      return True
    else:
      return False

  def getCurrentRun(self, model):
    self.cursor.execute("SELECT current_run from model where name='" + model + "'")
    rows = self.cursor.fetchall()
    currentRun = rows[0][0]
    return currentRun

  def updateModelRun(self):
    return