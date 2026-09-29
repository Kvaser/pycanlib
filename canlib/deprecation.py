"""helper module for handling deprecation via the standard warnings module

The first time any function marked in this module is called, a RuntimeWarning
will be issued. This is because DeprecationWarnings are hidden by default while
RuntimeWarnings are not. The RuntimeWarning explains to run python with the -Wd
flag to show DeprecationWarnings.

Note:

    All decorators in this module (and most other) must be placed before
    (below) any `staticmethod` and `classmethod` decorators, as those
    decorators do not wrap the functions well enough for `deprecation` to
    function.

To simply mark a function as deprecated, just decorate it with this module's
`deprecated` decorator::

  @deprecated
  def function():
    ...

This will produce a simple warning that the function is deprecated. If you want
to be a little more helpful, you can also tell your users what function to use
instead::

  @deprecated.favour("new_function")
  def function():
    ...

This will produce a warning that tells the user to use whatever is supplied as
the first argument instead of the decorated function.

Alternatively, in the case of a function being renamed, one can use::

  @deprecated.replacedby(new_function):
  def function():
    pass

This will completely replace the decorated function with a dummy function that
first warns about the use of the deprecated name, and then calls the function
supplied as the first argument to the decorator.

If only certain uses a function are deprecated the `manual_warn` function can
be called when something deprecated is used, passing the full message to be
displayed::

  def function(arg=None):
    if arg is None:
       manual_warn("Calling function without arg is deprecated")

If classes are renamed, their old names can be deprecated with::

  Class = class_replaced("Class", NewClass)

Likewise, class attributes can be deprecated with::

  class Class:
    attr = attr_replaced("attr", "new_attr")

"""

import functools
import textwrap
import warnings


class KvWarning(Warning):
    """Base class for all canlib warnings"""

    pass


class KvDeprecationBase(Warning):
    """Base class for canlib warnings related to deprecation"""

    pass


class KvDeprecationWarning(KvDeprecationBase, DeprecationWarning):
    """canlib equivalent of standard DeprecationWarning"""

    pass


class KvDeprecatedUsage(KvDeprecationBase, RuntimeWarning):
    """Special RuntimeWarning emitted on first KvDeprecationWarning"""

    pass


def manual_warn(message, stacklevel=3):
    """Manually warn using this module

    Any calls to this function qualifies as the "first" call in terms of
    raising a KvDeprecatedUsage.

    Args:
        message (str): used to initialize a KvDeprecationWarning
        stacklevel (int) [optional]: passed on to `warnings.warn`

    """
    deprecated._any_called()
    warnings.warn(KvDeprecationWarning(message), stacklevel=stacklevel)


def attr_replaced(original, replacement):
    """Create a `property` object representing a deprecated attribute

    Provides a getter, setter, and docstring.

    Args:
        original (str): the name of the deprecated attribute
        replacement (str): the name of the new attribute, to be used instead
    """

    def fget(self):
        manual_warn(
            f"Accessing {original} is deprecated, use {replacement} instead"
        )
        return getattr(self, replacement)

    def fset(self, val):
        manual_warn(
            f"Accessing {original} is deprecated, use {replacement} instead"
        )
        setattr(self, replacement, val)

    doc = f"Deprecated name for `{replacement}`"

    return property(fget=fget, fset=fset, doc=doc)


def class_replaced(original, new, replacement=None):
    """Create a deprecated class that preserves backwards compatibility

    Args:
        original (str): the name of the deprecated class
        new: the new class that replaces this one
        replacement (str) [optional]: the name of the new class, by default
            inferred from `new` argument
    """
    if replacement is None:
        replacement = new.__name__

    def init_moved_class(self, *args, **kwargs):
        manual_warn(
            f"{original} is deprecated, please use {replacement} instead"
        )
        return new.__init__(self, *args, **kwargs)

    docparagraph = (
        "    `{old}` has been renamed `{new}`, using the old name (`{old}`) is deprecated."
    ).format(old=original, new=replacement)

    docparagraph = textwrap.fill(docparagraph, width=79, subsequent_indent="    ")

    docstring = f"Deprecated name for `{replacement}`\n\n{docparagraph}\n\n    "

    newcls = type(original, (new, object), {'__init__': init_moved_class, '__doc__': docstring})

    return newcls


class deprecated:
    """Decorator for deprecating functions

    Also provides several class methods for alternate ways to wrap functions
    (or classes).

    """

    _replacement = None
    _first = True

    @classmethod
    def cls(cls, replacement):
        """Wrap a class's `__init__` function as deprecated

        Args:
            replacement (str): the name of the new class
        """

        def expanded(old):
            obj = cls(old.__init__)
            old.__init__ = obj
            obj.__name__ = old.__name__
            obj._replacement = replacement
            return obj

        return expanded

    @classmethod
    def favour(cls, replacement):
        """Wraps a function as deprecated

        Args:
            replacement (str): the name of the new function
        """

        def expanded(func):
            obj = cls(func)
            obj._replacement = replacement
            return obj

        return expanded

    @classmethod
    def replacedby(cls, new, replacement=None):
        """Wraps a function as deprecated, completely replacing it

        A function wrapped with this is never actually executed; when called,
        the call is delegated to the new function instead.

        Args:
            original (str): the name of the deprecated function
            new: the new function that replaces this one
            replacement (str) [optional]: the name of the new function, by default
                inferred from `new` argument

        """

        def expanded(old):
            obj = cls(old)
            obj.func = new
            obj._replacement = replacement or new.__name__
            return obj

        return expanded

    def __init__(self, func):
        """Wraps a function as deprecated"""
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        self._any_called()
        if self._replacement is None:
            msg = self.__name__ + " has been deprecated!"
        else:
            msg = "{f} has been deprecated, use {r} instead!".format(
                f=self.__name__,
                r=self._replacement,
            )
        warnings.warn(KvDeprecationWarning(msg), stacklevel=2)
        ret = self.func(*args, **kwargs)
        return ret

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return functools.partial(self, instance)

    @classmethod
    def _any_called(cls):
        if cls._first:
            warnings.warn(
                KvDeprecatedUsage(
                    "A deprecated function was called! "
                    + "Run python with -Wd flag for more information."
                )
            )
            cls._first = False
