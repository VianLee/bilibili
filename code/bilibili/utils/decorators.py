from inspect import signature
from functools import wraps


def typeassert(*t_args, **t_kwargs):
	'''Enforce type check on function using decorator.

	Todo
	=======
	Check the type of return value.

	References
	=======
	(Python Cookbook)[https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p07_enforcing_type_check_on_function_using_decorator.html]
	'''
	def decorate(func):
		# If in optimized mode, disable type checking
		if not __debug__:
			return func

		# Map function argument names to supplied types
		σ = signature(func)
		bound_types = σ.bind_partial(*t_args, **t_kwargs).arguments

		@wraps(func)
		def wrapper(*args, **kwargs):
			bound_values = σ.bind(*args, **kwargs)
			# Enforce type assertions across supplied arguments
			for name, value in bound_values.arguments.items():
				if name in bound_types:
					if not isinstance(value, bound_types[name]):
						raise TypeError(
							'Argument `{}` must be {}.'.format(name, bound_types[name])
						)
			return func(*args, **kwargs)
		return wrapper
	return decorate


def lazy_property(func):
    '''Lazy property.

    References
    =======
    (Python Cookbook)[https://python3-cookbook.readthedocs.io/zh_CN/latest/c08/p10_using_lazily_computed_properties.html]

    Example
    =======
        >>> import math
        >>> class Circle:
        ... 	def __init__(self, radius):
        ... 		self.radius = radius
        ... 	@lazy_property
        ... 	def area(self):
        ... 		print('Computing area')
        ... 		return math.pi * self.radius**2
    '''
    name = '_lazy_' + func.__name__
    @property
    def lazy(self):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            value = func(self)
            setattr(self, name, value)
            return value
    return lazy
