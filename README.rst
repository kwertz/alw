=====================================
alw: Simple dynamic loader for OpenAL
=====================================

Introduction
------------

alw_ is the easiest way to get your hands on the functionality offered by the
OpenAL_ API.

Its main part is a simple alw_gen.py_ Python script that generates alw.h and alw.c
from the `OpenAL headers`_ (al.h, alc.h and efx.h).
Those files can then be added and linked (statically or dynamically) into your
project.

Requirements
------------

alw_gen.py_ requires Python version 2.6 or newer.
It is also compatible with Python 3.x.

Example
-------

Here is a simple example of loading and using the OpenAL API via alw_.
Note that AL/alw.h must be included before any other OpenAL related headers::

    #include <stdio.h>
    #include <AL/alw.h>

    // ...

    int main(int argc, char* argv[])
    {
            ALCdevice* dev;
            ALCcontext* ctx;

            if (alwInit() < 0) {
                fprintf(stderr, "Failed to load OpenAL\n");
                return 1;
            }

            // error checking omitted
            dev = alcOpenDevice(0);
            ctx = alcCreateContext(dev, 0);
            alcMakeContextCurrent(ctx);

            // use OpenAL...

            // clean up
            alcMakeContextCurrent(0);
            alcDestroyContext(ctx);
            alcCloseDevice(dev);

            alwTerminate();

            return 0;
    }

API Reference
-------------

The alw_ API consists of just three functions:

``int alwInit(void)``

    Initializes the library. Should be called before any call to an OpenAL entry
    point is made. Returns ``0`` when alw_ was initialized successfully or a
    negative value if there was an error.

``int alwInitEfx(void)``

    Loads the EFX extension entry points. Should be called after creating an OpenAL
    context. Returns ``0`` when the EFX extension was loaded successfully or a
    negative value if there was an error.

``void alwTerminate(void)``

    Terminates the library and unloads the OpenAL module if possible.

License
-------

alw_ is in the public domain. See the file UNLICENSE for more information.

Credits
-------

Slavomir Kaslev <slavomir.kaslev@gmail.com>
    gl3w_, which alw is based on

Niklas F. Pluem <niklas.crossedwires@gmail.com>
    Implementation

Copyright
---------

OpenAL is a trademark of `Creative Labs`_, Inc.

.. _alw: https://github.com/kwertz/alw
.. _alw_gen.py: https://github.com/kwertz/alw/blob/master/alw_gen.py
.. _gl3w: https://github.com/skaslev/gl3w
.. _OpenAL headers: https://github.com/kcat/openal-soft/blob/master/include/AL
.. _OpenAL: http://www.openal.org/
.. _Creative Labs: http://www.creative.com/
.. _Loki Software: http://www.lokigames.com/
