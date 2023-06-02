import os, sys, re

class Symbol:
  def __init__(self, symbol, ns, file):
    self.symbol = symbol
    if ns is None:
      raise TypeError("'ns' is None")
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
      return self.ns + "." + self.symbol

  @property
  def alias(self):
    return "".join([word[0] for word in self.ns.split(".")]) + "s_" + self.symbol
