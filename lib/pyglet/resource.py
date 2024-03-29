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

'''Load application resources from a known path.

Loading resources by specifying relative paths to filenames is often
problematic in Python, as the working directory is not necessarily the same
directory as the application's script files.

This module allows applications to specify a search path for resources.
Relative paths are taken to be relative to the application's __main__ module.
ZIP files can appear on the path; they will be searched inside.  The resource
module also behaves as expected when applications are bundled using py2exe or
py2app.

As well as providing file references (with the `file` function), the resource
module also contains convenience functions for loading images, textures,
fonts, media and documents.

3rd party modules or packages not bound to a specific application should
construct their own `Loader` instance and override the path to use the
resources in the module's directory.

Path format
^^^^^^^^^^^

The resource path `path` (see also `Loader.__init__` and `Loader.path`)
is a list of locations to search for resources.  Locations are searched in the
order given in the path.  If a location is not valid (for example, if the
directory does not exist), it is skipped.

Locations in the path beginning with an ampersand (''@'' symbol) specify
Python packages.  Other locations specify a ZIP archive or directory on the
filesystem.  Locations that are not absolute are assumed to be relative to the
script home.  Some examples::

    # Search just the `res` directory, assumed to be located alongside the
    # main script file.
    path = ['res'] 

    # Search the directory containing the module `levels.level1`, followed
    # by the `res` directory.
    path = ['@levels.level1', 'res']

Paths are always case-sensitive, even if the filesystem is not.  This
avoids a common programmer error when porting applications between platforms.

The default path is ``['.']``.  If you modify the path, you must call
`reindex`.

:since: pyglet 1.1
'''

__docformat__ = 'restructuredtext'
__version__ = '$Id: $'

import operator
import os
import weakref
import sys
import zipfile
import StringIO

import pyglet

class ResourceNotFoundException(Exception):
    '''The named resource was not found on the search path.'''
    def __init__(self, name):
        message = ('Resource "%s" was not found on the path.  '
            'Ensure that the filename has the correct captialisation.') % name
        Exception.__init__(self, message)

def get_script_home():
    '''Get the directory containing the program entry module.

    For ordinary Python scripts, this is the directory containing the
    ``__main__`` module.  For executables created with py2exe the result is
    the directory containing the running executable file.  For OS X bundles
    created using Py2App the result is the Resources directory within the
    running bundle.

    If none of the above cases apply and the file for ``__main__`` cannot
    be determined the working directory is returned.

    :rtype: str
    '''

    frozen = getattr(sys, 'frozen', None)
    if frozen in ('windows_exe', 'console_exe'):
        return os.path.dirname(sys.executable)
    elif frozen == 'macosx_app':
        return os.environ['RESOURCEPATH']
    else:
        main = sys.modules['__main__']
        if hasattr(main, '__file__'):
            return os.path.dirname(main.__file__)

    # Probably interactive
    return ''

def get_settings_path(name):
    '''Get a directory to save user preferences.

    Different platforms have different conventions for where to save user
    preferences, saved games, and settings.  This function implements those
    conventions.  Note that the returned path may not exist: applications
    should use ``os.makedirs`` to construct it if desired.

    On Linux, a hidden directory `name` in the user's home directory is
    returned.

    On Windows (including under Cygwin) the `name` directory in the user's
    ``Application Settings`` directory is returned.

    On Mac OS X the `name` directory under ``~/Library/Application Support``
    is returned.

    :Parameters:
        `name` : str
            The name of the application.

    :rtype: str
    '''
    if sys.platform in ('cygwin', 'win32'):
        if 'APPDATA' in os.environ:
            return os.path.join(os.environ['APPDATA'], name)
        else:
            return os.path.expanduser('~/%s' % name)
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/%s' % name)
    else:
        return os.path.expanduser('~/.%s' % name)

class Location(object):
    '''Abstract resource location.

    Given a location, a file can be loaded from that location with the `open`
    method.  This provides a convenient way to specify a path to load files
    from, and not necessarily have that path reside on the filesystem.
    '''
    def open(self, filename, mode='rb'):
        '''Open a file at this locaiton.

        :Parameters:
            `filename` : str
                The filename to open.  Absolute paths are not supported.
                Relative paths are not supported by most locations (you
                should specify only a filename with no path component).
            `mode` : str
                The file mode to open with.  Only files opened on the
                filesystem make use of this parameter; others ignore it.

        :rtype: file object
        '''
        raise NotImplementedError('abstract')

class FileLocation(Location):
    '''Location on the filesystem.
    '''
    def __init__(self, path):
        '''Create a location given a relative or absolute path.

        :Parameters:
            `path` : str
                Path on the filesystem.
        '''
        self.path = path

    def open(self, filename, mode='rb'):
        return open(os.path.join(self.path, filename), mode)

class ZIPLocation(Location):
    '''Location within a ZIP file.
    '''
    def __init__(self, zip, dir):
        '''Create a location given an open ZIP file and a path within that
        file.

        :Parameters:
            `zip` : ``zipfile.ZipFile``
                An open ZIP file from the ``zipfile`` module.
            `dir` : str
                A path within that ZIP file.  Can be empty to specify files at
                the top level of the ZIP file.

        '''
        self.zip = zip
        self.dir = dir
        
    def open(self, filename, mode='rb'):
        path = os.path.join(self.dir, filename)
        text = self.zip.read(path)
        return StringIO.StringIO(text)
        
class URLLocation(Location):
    '''Location on the network.

    This class uses the ``urlparse`` and ``urllib2`` modules to open files on
    the network given a URL.
    '''
    def __init__(self, base_url):
        '''Create a location given a base URL.

        :Parameters:
            `base_url` : str
                URL string to prepend to filenames.

        '''
        self.base = base_url

    def open(self, filename, mode='rb'):
        import urlparse
        import urllib2
        url = urlparse.urljoin(self.base, filename)
        return urllib2.urlopen(url)

class Loader(object):
    '''Load program resource files from disk.

    The loader contains a search path which can include filesystem
    directories, ZIP archives and Python packages.

    :Ivariables:
        `path` : list of str
            List of search locations.  After modifying the path you must
            call the `reindex` method.
        `script_home` : str
            Base resource location, defaulting to the location of the
            application script.

    '''
    def __init__(self, path=None, script_home=None):
        '''Create a loader for the given path.

        If no path is specified it defaults to ``['.']``; that is, just the
        program directory.

        See the module documentation for details on the path format.

        :Parameters:
            `path` : list of str
                List of locations to search for resources.
            `script_home` : str
                Base location of relative files.  Defaults to the result of
                `get_script_home`.

        '''
        if path is None:
            path = ['.']
        if type(path) in (str, unicode):
            path = [path]
        self.path = list(path)
        if script_home is None:
            script_home = get_script_home()
        self._script_home = script_home
        self.reindex()

        # Map name to image
        self._cached_textures = weakref.WeakValueDictionary()
        self._cached_images = weakref.WeakValueDictionary()
        self._cached_animations = weakref.WeakValueDictionary()

        # Map bin size to list of atlases
        self._texture_atlas_bins = {}

    def reindex(self):
        '''Refresh the file index.

        You must call this method if `path` is changed or the filesystem
        layout changes.
        '''
        self._index = {}
        for path in self.path:
            if path.startswith('@'):
                # Module
                name = path[1:]

                try:
                    module = __import__(name)
                except:
                    continue

                for component in name.split('.')[1:]:
                    module = getattr(module, component)

                if hasattr(module, '__file__'):
                    path = os.path.dirname(module.__file__)
                else:
                    path = '' # interactive
            elif not os.path.isabs(path):
                # Add script base unless absolute
                assert '\\' not in path, \
                    'Backslashes not permitted in relative path'
                path = os.path.join(self._script_home, path)

            if os.path.isdir(path):
                # Filesystem directory
                location = FileLocation(path)
                for name in os.listdir(path):
                    self._index_file(name, location)
            else:
                # Find path component that is the ZIP file.
                dir = ''
                while path and not os.path.isfile(path):
                    path, tail_dir = os.path.split(path)
                    dir = '/'.join((tail_dir, dir))
                dir = dir.rstrip('/')

                # path is a ZIP file, dir resides within ZIP
                if path and zipfile.is_zipfile(path):
                    zip = zipfile.ZipFile(path, 'r')
                    location = ZIPLocation(zip, dir)
                    for name_path in zip.namelist():
                        name_dir, name = os.path.split(name_path)
                        assert '\\' not in name_dir
                        assert not name_dir.endswith('/')
                        if name_dir == dir:
                            self._index_file(name, location)

    def _index_file(self, name, location):
        if name not in self._index:
            self._index[name] = location

    def file(self, name, mode='rb'):
        '''Load a resource.

        :Parameters:
            `name` : str
                Filename of the resource to load.
            `mode` : str
                Combination of ``r``, ``w``, ``a``, ``b`` and ``t`` characters
                with the meaning as for the builtin ``open`` function.

        :rtype: file object
        '''
        try:
            location = self._index[name]
            return location.open(name, mode)
        except KeyError:
            raise ResourceNotFoundException(name)

    def location(self, name):
        '''Get the location of a resource.

        This method is useful for opening files referenced from a resource.
        For example, an HTML file loaded as a resource might reference some
        images.  These images should be located relative to the HTML file, not
        looked up individually in the loader's path.

        :Parameters:
            `name` : str
                Filename of the resource to locate.

        :rtype: `Location`
        '''
        try:
            return self._index[name]
        except KeyError:
            raise ResourceNotFoundException(name)

    def add_font(self, name):
        '''Add a font resource to the application.

        Fonts not installed on the system must be added to pyglet before they
        can be used with `font.load`.  Although the font is added with
        its filename using this function, it is loaded by specifying its
        family name.  For example::

            resource.add_font('action_man.ttf')
            action_man = font.load('Action Man')

        :Parameters:
            `name` : str
                Filename of the font resource to add.

        '''
        from pyglet import font
        file = self.file(name)
        font.add_file(file)

    def _alloc_image(self, name):
        file = self.file(name)
        img = pyglet.image.load(name, file=file)
        bin = self._get_texture_atlas_bin(img.width, img.height)
        if bin is None:
            return img.get_texture(True)

        return bin.add(img)

    def _get_texture_atlas_bin(self, width, height):
        '''A heuristic for determining the atlas bin to use for a given image
        size.  Returns None if the image should not be placed in an atlas (too
        big), otherwise the bin (a list of TextureAtlas).
        ''' 
        # Large images are not placed in an atlas
        if width > 128 or height > 128:
            return None

        # Group images with small height separately to larger height (as the
        # allocator can't stack within a single row).
        bin_size = 1
        if height > 32:
            bin_size = 2

        try:
            bin = self._texture_atlas_bins[bin_size]
        except KeyError:
            bin = self._texture_atlas_bins[bin_size] = \
                pyglet.image.atlas.TextureBin()

        return bin

    def image(self, name, flip_x=False, flip_y=False, rotate=0):
        '''Load an image with optional transformation.

        This is similar to `texture`, except the resulting image will be
        packed into a `TextureBin` if it is an appropriate size for packing.
        This is more efficient than loading images into separate textures.

        :Parameters:
            `name` : str
                Filename of the image source to load.
            `flip_x` : bool
                If True, the returned image will be flipped horizontally.
            `flip_y` : bool
                If True, the returned image will be flipped vertically.
            `rotate` : int
                The returned image will be rotated clockwise by the given
                number of degrees (a mulitple of 90).

        :rtype: `Texture`
        :return: A complete texture if the image is large, otherwise a
            `TextureRegion` of a texture atlas.
        '''
        if name in self._cached_images:
            identity = self._cached_images[name]
        else:
            identity = self._cached_images[name] = self._alloc_image(name)

        if not rotate and not flip_x and not flip_y:
            return identity
                
        return identity.get_transform(flip_x, flip_y, rotate)

    def animation(self, name, flip_x=False, flip_y=False, rotate=0):
        '''Load an animation with optional transformation.

        Animations loaded from the same source but with different
        transformations will use the same textures.

        :Parameters:
            `name` : str
                Filename of the animation source to load.
            `flip_x` : bool
                If True, the returned image will be flipped horizontally.
            `flip_y` : bool
                If True, the returned image will be flipped vertically.
            `rotate` : int
                The returned image will be rotated clockwise by the given
                number of degrees (a mulitple of 90).

        :rtype: `Animation`
        '''
        try:
            identity = self._cached_animations[name]
        except KeyError:
            animation = pyglet.image.load_animation(name, self.file(name))
            bin = self._get_texture_atlas_bin(animation.get_max_width(), 
                                              animation.get_max_height())
            if bin:
                animation.add_to_texture_bin(bin)

            identity = self._cached_animations[name] = animation

        if not rotate and not flip_x and not flip_y:
            return identity
                
        return identity.get_transform(flip_x, flip_y, rotate)
       
    def get_cached_image_names(self):
        '''Get a list of image filenames that have been cached.

        This is useful for debugging and profiling only.

        :rtype: list
        :return: List of str
        '''
        return self._cached_images.keys()

    def get_cached_animation_names(self):
        '''Get a list of animation filenames that have been cached.

        This is useful for debugging and profiling only.

        :rtype: list
        :return: List of str
        '''
        return self._cached_animations.keys()

    def get_texture_bins(self):
        '''Get a list of texture bins in use.

        This is useful for debugging and profiling only.

        :rtype: list
        :return: List of `TextureBin`
        '''
        return self._texture_atlas_bins.values()
       
    def media(self, name, streaming=True):
        '''Load a sound or video resource.

        The meaning of `streaming` is as for `media.load`.  Compressed
        sources cannot be streamed (that is, video and compressed audio
        cannot be streamed from a ZIP archive).

        :Parameters:
            `name` : str
                Filename of the media source to load.
            `streaming` : bool
                True if the source should be streamed from disk, False if
                it should be entirely decoded into memory immediately.

        :rtype: `media.Source`
        '''
        from pyglet import media
        try:
            location = self._index[name]
            if isinstance(location, FileLocation):
                # Don't open the file if it's streamed from disk -- AVbin
                # needs to do it.
                path = os.path.join(location.path, name)
                return media.load(path, streaming=streaming)
            else:
                file = location.open(name)
                return media.load(name, file=file, streaming=streaming)
        except KeyError:
            raise ResourceNotFoundException(name)

    def texture(self, name):
        '''Load a texture.

        The named image will be loaded as a single OpenGL texture.  If the
        dimensions of the image are not powers of 2 a `TextureRegion` will
        be returned.

        :Parameters:
            `name` : str
                Filename of the image resource to load.

        :rtype: `Texture`
        '''
        if name in self._cached_textures:
            return self._cached_textures[name]

        file = self.file(name)
        texture = pyglet.image.load(name, file=file).get_texture()
        self._cached_textures[name] = texture
        return texture

    def html(self, name):
        '''Load an HTML document.

        :Parameters:
            `name` : str
                Filename of the HTML resource to load.

        :rtype: `FormattedDocument`
        '''
        file = self.file(name)
        return pyglet.text.decode_html(file.read(), self.location(name))

    def attributed(self, name):
        '''Load an attributed text document.

        See `pyglet.text.formats.attributed` for details on this format.

        :Parameters:
            `name` : str
                Filename of the attribute text resource to load.

        :rtype: `FormattedDocument`
        '''
        file = self.file(name)
        return pyglet.text.load(name, file, 'text/vnd.pyglet-attributed')

    def text(self, name):
        '''Load a plain text document.

        :Parameters:
            `name` : str
                Filename of the plain text resource to load.

        :rtype: `UnformattedDocument`
        '''
        file = self.file(name)
        return pyglet.text.load(name, file, 'text/plain')

    def get_cached_texture_names(self):
        '''Get the names of textures currently cached.

        :rtype: list of str
        '''
        return self._cached_textures.keys()

#: Default resource search path.
#:
#: Locations in the search path are searched in order and are always
#: case-sensitive.  After changing the path you must call `reindex`.
#:
#: See the module documentation for details on the path format.
#:
#: :type: list of str
path = []

class _DefaultLoader(Loader):
    def _get_path(self):
        return path

    def _set_path(self, value):
        global path
        path = value

    path = property(_get_path, _set_path)

_default_loader = _DefaultLoader()
reindex = _default_loader.reindex
file = _default_loader.file
location = _default_loader.location
add_font = _default_loader.add_font
image = _default_loader.image
animation = _default_loader.animation
get_cached_image_names = _default_loader.get_cached_image_names
get_cached_animation_names = _default_loader.get_cached_animation_names
get_texture_bins = _default_loader.get_texture_bins
media = _default_loader.media
texture = _default_loader.texture
html = _default_loader.html
attributed = _default_loader.attributed
text = _default_loader.text
get_cached_texture_names = _default_loader.get_cached_texture_names
