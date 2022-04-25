""" Implementation of a plot managing class. """
import matplotlib.pyplot as plt
from .helpers import cm2inch
from .singleton import Singleton


class PlotHelper(metaclass=Singleton):
	""" Singleton class to manage various plots used throughout the STL implementation """

	def __init__(self):
		self.__figure = None
		self.__axs = None
		self.__index = 0

	def reset(self):
		""" Reset the plots to None/empty"""
		if self.__figure is not None:
			for f in self.__figure:
				f.close()
		self.__figure = None
		self.__axs = None
		self.__index = 0

	def createSubplots(self, count):
		""" Add a subplot to the current figure """
		self.__figure, self.__axs = plt.subplots(count, sharex=True, sharey=True)
		self.__figure.set_size_inches(cm2inch(15), cm2inch(count * 3))

	def booleanPlot(self, xValues, yValues, title, fmt='r-'):
		""" Plot a boolean Signal (step fn) """
		assert self.__figure is not None and self.__axs is not None
		self.__axs[self.__index].step(xValues, yValues, fmt, where='post')
		self.__genericPlotTasks(title)

	def quantitativePlot(self, xValues, yValues, title, fmt='r-'):
		""" Plot a quantitative signal (line) """
		assert self.__figure is not None and self.__axs is not None
		self.__axs[self.__index].plot(xValues, yValues, fmt)
		self.__genericPlotTasks(title)

	def __genericPlotTasks(self, title):
		""" Helper function for plotting; common between quant and boolean """
		self.__axs[self.__index].set_title(title)
		self.__index += 1

	# pylint: disable=no-self-use
	def show(self):
		""" Show the created figure. """
		plt.show()

	# pylint: enable=no-self-use
