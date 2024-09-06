from contextvars import ContextVar, copy_context
from starlette.types import ASGIApp, Receive, Scope, Send
from typing import Dict, Any, Iterator, Tuple

class Globals:
    """
    A class for managing global variables with context isolation.

    Provides methods to set, get, and manage variables in a request-specific context.
    """

    __slots__ = ("_context_data",)

    _context_data: ContextVar[Dict[str, Any]]

    def __init__(self) -> None:
        """Initialize the Globals instance with an empty variable store."""
        object.__setattr__(self, '_context_data', ContextVar("context_data", default={}))

    def clear(self) -> None:
        """Clear all context variables from the store."""
        self._context_data.set({})

    def __getattr__(self, name: str) -> Any:
        """
        Retrieve the value of a variable.

        Args:
            name: The name of the variable.

        Raises:
            AttributeError: If the variable is not found.

        Returns:
            The value of the variable.
        """
        try:
            return self._context_data.get()[name]
        except KeyError:
            raise AttributeError(f"'{name}' variable does not exist in globals, make sure to set it before trying to use it")

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set the value of a variable.

        Args:
            name: The name of the variable.
            value: The value to set.
        """
        self._context_data.get()[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        """
        Retrieve the value of a variable with an optional default value.

        Args:
            name: The name of the variable.
            default: The value to return if the variable is not found.

        Returns:
            The value of the variable or the default value.
        """
        return self._context_data.get().get(name, default)

    def pop(self, name: str, default: Any = None) -> Any:
        """
        Retrieve and remove the value of a variable, with an optional default.

        Args:
            name: The name of the variable.
            default: The value to return if the variable is not found.

        Returns:
            The value of the variable or the default value.
        """
        return self._context_data.get().pop(name, default)

    def __contains__(self, name: str) -> bool:
        """
        Check if a variable exists.

        Args:
            name: The name of the variable.

        Returns:
            True if the variable exists, False otherwise.
        """
        return name in self._context_data.get()

    def keys(self) -> Iterator[str]:
        """
        Return an iterator over the variable names.

        Returns:
            An iterator over the variable names.
        """
        return iter(self._context_data.get().keys())

    def values(self) -> Iterator[Any]:
        """
        Return an iterator over the variable values.

        Returns:
            An iterator over the variable values.
        """
        return iter(self._context_data.get().values())

    def items(self) -> Iterator[Tuple[str, Any]]:
        """
        Return an iterator over the variable name-value pairs.

        Returns:
            An iterator over tuples containing variable names and values.
        """
        return iter(self._context_data.get().items())

    def to_dict(self) -> Dict[str, Any]:
        """
        Return all variables and their current values as a dictionary.

        Returns:
            A dictionary of variable names and their values.
        """
        return dict(self._context_data.get())


class GlobalsMiddleware:
    """
    Middleware to handle global variables context for each request.

    Ensures that each request operates with a fresh context for global variables.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the middleware with the ASGI application.

        Args:
            app: The ASGI application to wrap.
        """
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle an ASGI request.

        Clears the global context and runs the ASGI application in a new context.

        Args:
            scope: The ASGI scope.
            receive: The ASGI receive function.
            send: The ASGI send function.
        """
        # Clear global variables for the request
        g.clear()
        # Create a new context for the request
        ctx = copy_context()
        # Run the original ASGI app in the new context
        await ctx.run(self.app, scope, receive, send)


# Global instance of Globals to be used by the middleware and users
g = Globals()
