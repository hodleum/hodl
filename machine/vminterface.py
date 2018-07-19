"""
@title HODL API to external VMs
@version 0.1
"""
class DMemSys():
  def __init__(self):
    pass
  
  """
  Low-level stuff
  """
  def __setitem__(self, index, val, options=None):
    pass
  def __getitem__(self, index):
    pass
  def __createitem__(self, index):
    pass
  def __delitem__(self, index):
    pass
  
  """
  High-level stuff
  """
  def setItem(self, name, val, time_of_life=-1):
    pass
  def getItem(self, name):
    pass
  def delItem(self, name):
    pass
