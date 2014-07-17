import psycopg2

class NgwipsDB:

  def __init__(self, dbConnStr):
    self.conn = psycopg2.connect(dbConnStr)
    self.cursor = self.conn.cursor()
    return

  def isNewRun(self, model, currentRun):
    self.cursor.execute("SELECT current_run from model where name='" + model + "'")
    rows = self.cursor.fetchall()

    # If it is a new run... return True.
    if int(rows[0][0]) < int(currentRun):
      return True
    else:
      return False

  def updateModelRun(self):
    return