class Symbol:
  def __init__(self, symbol, ns, file):
    self.symbol = symbol
    self.ns = ns
    self.file = file

  def __hash__(self):
    return hash(self.address)

  def __eq__(self, other):
    if isinstance(other, Symbol):
      return hash(self) == hash(other)
    return False

  def __repr__(self):
    return self.address

  def __str__(self):
    return self.address

  @property
  def address(self):
    try:
      return self.ns + "." + self.symbol
    except Exception as ex:
      print(self.symbol, self.file)
      raise ex
