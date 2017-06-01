"""AsyncIO support for zmq

Requires asyncio and Python 3.
"""

# Copyright (c) PyZMQ Developers.
# Distributed under the terms of the Modified BSD License.
# Derived from Python 3.5.1 selectors._BaseSelectorImpl, used under PSF License

from collections import Mapping
import warnings

import zmq as _zmq
from zmq.eventloop import future as _future

# TODO: support trollius for Legacy Python? (probably not)

import asyncio
from asyncio import SelectorEventLoop, Future
try:
    import selectors
except ImportError:
    from asyncio import selectors # py33


class _AsyncIO(object):
    _Future = Future
    _WRITE = selectors.EVENT_WRITE
    _READ = selectors.EVENT_READ

    def _default_loop(self):
        return asyncio.get_event_loop()

class Poller(_AsyncIO, _future._AsyncPoller):
    """Poller returning asyncio.Future for poll results."""
    def _watch_raw_socket(self, loop, socket, evt, f):
        """Schedule callback for a raw socket"""
        if evt & self._READ:
            loop.add_reader(socket, lambda *args: f())
        if evt & self._WRITE:
            loop.add_writer(socket, lambda *args: f())

    def _unwatch_raw_sockets(self, loop, *sockets):
        """Unschedule callback for a raw socket"""
        for socket in sockets:
            loop.remove_reader(socket)
            loop.remove_writer(socket)


class Socket(_AsyncIO, _future._AsyncSocket):
    """Socket returning asyncio Futures for send/recv/poll methods."""

    _poller_class = Poller

    def _init_io_state(self):
        """initialize the ioloop event handler"""
        self.io_loop.add_reader(self._shadow_sock, lambda : self._handle_events(0, 0))

    def _clear_io_state(self):
        """clear any ioloop event handler

        called once at close
        """
        self.io_loop.remove_reader(self._shadow_sock)

class Context(_zmq.Context):
    """Context for creating asyncio-compatible Sockets"""
    _socket_class = Socket


class ZMQEventLoop(SelectorEventLoop):
    """AsyncIO eventloop using zmq_poll"""
    def __init__(self, selector=None):
        import warnings
        warnings.warn("""ZMQEventLoop is deprecated in pyzmq 17 and no longer required.""", DeprecationWarning)
        return super(ZMQEventLoop, self).__init__(selector)


_loop = None

def install():
    """DEPRECATED: No longer needed in pyzmq 17"""
    warnings.warn("""zmq.asyncio.install is deprecated in pyzmq 17 and no longer required.""",
        DeprecationWarning,
    )


__all__ = [
    'Context',
    'Socket',
    'Poller',
    'ZMQEventLoop',
    'install',
]
