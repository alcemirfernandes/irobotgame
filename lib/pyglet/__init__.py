# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

'''pyglet is a cross-platform games and multimedia package.

Detailed documentation is available at http://www.pyglet.org
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: __init__.py 1981 2008-03-29 01:16:02Z Alex.Holkner $'

import os
import sys

_is_epydoc = hasattr(sys, 'is_epydoc') and sys.is_epydoc

#: The release version of this pyglet installation.  
#:
#: Valid only if pyglet was installed from a source or binary distribution
#: (i.e. not in a checked-out copy from SVN).
#: 
#: Use setuptools if you need to check for a specific release version, e.g.::
#:
#:    >>> import pyglet
#:    >>> from pkg_resources import parse_version
#:    >>> parse_version(pyglet.version) >= parse_version('1.0')
#:    True
#:
version = '1.1alpha2'

def _require_ctypes_version(version):
    # Check ctypes version
    import ctypes
    req = [int(i) for i in version.split('.')]
    have = [int(i) for i in ctypes.__version__.split('.')]
    if not tuple(have) >= tuple(req):
        raise ImportError('pyglet requires ctypes %s or later.' % version)
_require_ctypes_version('1.0.0')

_enable_optimisations = not __debug__
if getattr(sys, 'frozen', None):
    _enable_optimisations = True

#: Global dict of pyglet options.  To change an option from its default, you
#: must import ``pyglet`` before any sub-packages.  For example::
#:
#:      import pyglet
#:      pyglet.options['debug_gl'] = False
#:
#: The default options can be overridden from the OS environment.  The
#: corresponding environment variable for each option key is prefaced by
#: ``PYGLET_``.  For example, in Bash you can set the ``debug_gl`` option with::
#:
#:      PYGLET_DEBUG_GL=True; export PYGLET_DEBUG_GL
#: 
#: For options requiring a tuple of values, separate each value with a comma.
#:
#: The non-development options are:
#:
#: audio
#:     A sequence of the names of audio modules to attempt to load, in
#:     order of preference.  Valid driver names are:
#:
#:     * directsound, the Windows DirectSound audio module (Windows only)
#:     * alsa, the ALSA audio module (Linux only) 
#:     * openal, the OpenAL audio module
#:     * silent, no audio
#: debug_lib
#:     If True, prints the path of each dynamic library loaded.
#: debug_gl
#:     If True, all calls to OpenGL functions are checked afterwards for
#:     errors using ``glGetError``.  This will severely impact performance,
#:     but provides useful exceptions at the point of failure.  By default,
#:     this option is enabled if ``__debug__`` is (i.e., if Python was not run
#:     with the -O option).  It is disabled by default when pyglet is "frozen"
#:     within a py2exe or py2app library archive.
#: shadow_window
#:     By default, pyglet creates a hidden window with a GL context when
#:     pyglet.gl is imported.  This allows resources to be loaded before
#:     the application window is created, and permits GL objects to be
#:     shared between windows even after they've been closed.  You can
#:     disable the creation of the shadow window by setting this option to
#:     False.  Recommended for advanced devlopers only.
#:
#:     **Since:** pyglet 1.1
#: vsync
#:     If set, the `pyglet.window.Window.vsync` property is ignored, and
#:     this option overrides it (to either force vsync on or off).  If unset,
#:     or set to None, the `pyglet.window.Window.vsync` property behaves
#:     as documented.
#: xsync
#:     If set (the default), pyglet will attempt to synchronise the drawing of
#:     double-buffered windows to the border updates of the X11 window
#:     manager.  This improves the appearance of the window during resize
#:     operations.  This option only affects double-buffered windows on
#:     X11 servers supporting the Xsync extension with a window manager
#:     that implements the _NET_WM_SYNC_REQUEST protocol.
#:
#:     **Since:** pyglet 1.1
#:
options = {
    'audio': ('directsound', 'openal', 'alsa', 'silent'),
    'font': ('gdiplus', 'win32'), # ignored outside win32; win32 is deprecated
    'debug_font': False,
    'debug_gl': not _enable_optimisations,
    'debug_gl_trace': False,
    'debug_gl_trace_args': False,
    'debug_graphics_batch': False,
    'debug_lib': False,
    'debug_media': False,
    'debug_trace': False,
    'debug_trace_args': False,
    'debug_trace_depth': 1,
    'debug_win32': False,
    'debug_x11': False,
    'graphics_vbo': True,
    'shadow_window': True,
    'vsync': None,
    'xsync': True,
}

_option_types = {
    'audio': tuple,
    'font': tuple,
    'debug_font': bool,
    'debug_gl': bool,
    'debug_gl_trace': bool,
    'debug_gl_trace_args': bool,
    'debug_graphics_batch': bool,
    'debug_lib': bool,
    'debug_media': bool,
    'debug_trace': bool,
    'debug_trace_args': bool,
    'debug_trace_depth': int,
    'debug_win32': bool,
    'debug_x11': bool,
    'graphics_vbo': bool,
    'shadow_window': bool,
    'vsync': bool,
    'xsync': bool,
}

def _read_environment():
    '''Read defaults for options from environment'''
    for key in options:
        env = 'PYGLET_%s' % key.upper()
        try:
            value = os.environ['PYGLET_%s' % key.upper()]
            if _option_types[key] is tuple:
                options[key] = value.split(',')
            elif _option_types[key] is bool:
                options[key] = value in ('true', 'TRUE', 'True', '1')
            elif _option_types[key] is int:
                options[key] = int(value)
        except KeyError:
            pass
_read_environment()

if sys.platform == 'cygwin':
    # This hack pretends that the posix-like ctypes provides windows
    # functionality.  COM does not work with this hack, so there is no
    # DirectSound support.
    import ctypes
    ctypes.windll = ctypes.cdll
    ctypes.oledll = ctypes.cdll
    ctypes.WINFUNCTYPE = ctypes.CFUNCTYPE
    ctypes.HRESULT = ctypes.c_long

class _Module(object):
    '''Lazily import submodules when accessed as attributes.  
    
    Allows applications to use pyglet.window without importing the
    pyglet.window module directly.
    '''
    def __init__(self, submodules):
        m = sys.modules[__name__]
        for name in dir(m):
            setattr(self, name, getattr(m, name))
        self._name = __name__
        self._file = __file__
        self._submodules = submodules
   
        self._trace_args = options['debug_trace_args']
        self._trace_depth = options['debug_trace_depth']
        if options['debug_trace']:
            self._install_trace()

        if not _is_epydoc:
            sys.modules[__name__] = self

    def __getattr__(self, name):
        if name in self._submodules:
            m = __import__('.'.join((self._name, name)), {}, {}, ['foo'])
            return m
        raise AttributeError("'%s' has no attribute '%s'" % (self._name, name))

    def __repr__(self):
        return "<module '%s' from '%s' using class '%s'>" % (
            self._name, self._file, self.__class__.__name__)

    _trace_filename_abbreviations = {}

    def _trace_repr(self, value, size=40):
        value = repr(value)
        if len(value) > size:
            value = value[:size//2-2] + '...' + value[-size//2-1:]
        return value

    def _trace_frame(self, frame, indent):
        from pyglet import lib
        import os
        if frame.f_code is lib._TraceFunction.__call__.func_code:
            is_ctypes = True
            func = frame.f_locals['self']._func
            name = func.__name__
            location = '[ctypes]'
        else:
            is_ctypes = False
            code = frame.f_code
            name = code.co_name
            path = code.co_filename
            line = code.co_firstlineno
        
            try:
                filename = self._trace_filename_abbreviations[path]
            except KeyError: 
                # Trim path down
                dir = ''
                path, filename = os.path.split(path)
                while len(dir + filename) < 30:
                    filename = os.path.join(dir, filename)
                    path, dir = os.path.split(path)
                    if not dir:
                        filename = os.path.join('', filename)
                        break
                else:
                    filename = os.path.join('...', filename)
                self._trace_filename_abbreviations[path] = filename

            location = '(%s:%d)' % (filename, line)

        if indent:
            name = 'Called from %s' % name
        print '%s%s %s' % (indent, name, location)

        if self._trace_args:
            if is_ctypes:
                args = [self._trace_repr(arg) for arg in frame.f_locals['args']]
                print '  %sargs=(%s)' % (indent, ', '.join(args))
            else:
                for argname in code.co_varnames[:code.co_argcount]:
                    try:
                        argvalue = self._trace_repr(frame.f_locals[argname])
                        print '  %s%s=%s' % (indent, argname, argvalue)
                    except:
                        pass

    def _trace_func(self, frame, event, arg):
        if event == 'call':
            indent = ''
            for i in range(self._trace_depth):
                self._trace_frame(frame, indent)
                indent += '  '
                frame = frame.f_back
                if not frame:
                    break
                
        elif event == 'exception':
            (exception, value, traceback) = arg
            print 'First chance exception raised:', repr(exception)

    def _install_trace(self):
        sys.setprofile(self._trace_func)

_Module(
    ('app', 'clock', 'com', 'event', 'font', 'gl', 'graphics', 'image',
     'lib', 'media', 'resource', 'sprite', 'text', 'window')
)

# Fool py2exe, py2app into including all top-level modules (doesn't understand
# lazy loading)
if False:
    import app
    import clock
    import com
    import event
    import font
    import gl
    import graphics
    import image
    import lib
    import media
    import resource
    import sprite
    import text
    import window

# Hack around some epydoc bug that causes it to think pyglet.window is None.
if _is_epydoc:
    import window
