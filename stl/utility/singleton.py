""" A metaclass for defining singleton classes """


class Singleton(type):
	""" Metaclass to allow Singleton types. """
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]
