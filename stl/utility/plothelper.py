import matplotlib.pyplot as plt
from .helpers import cm2inch
from .singleton import Singleton

# Meta class 

class PlotHelper(metaclass=Singleton):
	def __init__(self):
		self.__figure = None
		self.__axs = None
		self.__index = 0

	def reset(self):
		if self.__figure is not None:
			for f in self.__figure:
				f.close()
		self.__figure = None
		self.__axs = None
		self.__index = 0

	def createSubplots(self, count):
		self.__figure, self.__axs = plt.subplots(count, sharex=True, sharey=True)
		self.__figure.set_size_inches(cm2inch(15), cm2inch(count * 3))


	def booleanPlot(self, xValues, yValues, title, format='r-'):
		assert self.__figure is not None and self.__axs is not None
		self.__axs[self.__index].step(xValues, yValues, format, where='post')
		self.__genericPlotTasks(title)

	def quantitativePlot(self, xValues, yValues, title, format='r-'):
		assert self.__figure is not None and self.__axs is not None
		self.__axs[self.__index].plot(xValues, yValues, format)
		self.__genericPlotTasks(title)

	def __genericPlotTasks(self, title):
		self.__axs[self.__index].set_title(title)
		self.__index += 1

	def show(self):
		plt.show()
