#!/usr/bin/env python

#   This file is part of alw, hosted at https://github.com/kwertz/alw
#   alw is based on gl3w, hosted at https://github.com/skaslev/gl3w
#
#   This is free and unencumbered software released into the public domain.
#
#   Anyone is free to copy, modify, publish, use, compile, sell, or
#   distribute this software, either in source code form or as a compiled
#   binary, for any purpose, commercial or non-commercial, and by any
#   means.
#
#   In jurisdictions that recognize copyright laws, the author or authors
#   of this software dedicate any and all copyright interest in the
#   software to the public domain. We make this dedication for the benefit
#   of the public at large and to the detriment of our heirs and
#   successors. We intend this dedication to be an overt act of
#   relinquishment in perpetuity of all present and future rights to this
#   software under copyright law.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#   OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#   OTHER DEALINGS IN THE SOFTWARE.

# Allow Python 2.6+ to use the print() function
from __future__ import print_function

import re
import os
import argparse

# UNLICENSE copyright header
UNLICENSE = br'''/*

	This file was generated with alw_gen.py, part of alw
	(hosted at https://github.com/kwertz/alw)

	alw is based on gl3w, hosted at https://github.com/skaslev/gl3w

	This is free and unencumbered software released into the public domain.

	Anyone is free to copy, modify, publish, use, compile, sell, or
	distribute this software, either in source code form or as a compiled
	binary, for any purpose, commercial or non-commercial, and by any
	means.

	In jurisdictions that recognize copyright laws, the author or authors
	of this software dedicate any and all copyright interest in the
	software to the public domain. We make this dedication for the benefit
	of the public at large and to the detriment of our heirs and
	successors. We intend this dedication to be an overt act of
	relinquishment in perpetuity of all present and future rights to this
	software under copyright law.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
	EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
	MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
	IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
	ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
	OTHER DEALINGS IN THE SOFTWARE.

*/

'''

output_dir = ""

argparser = argparse.ArgumentParser()
argparser.add_argument("--destdir", help="Path to the directory where the outputs should be written to")
args = argparser.parse_args()

if args.destdir:
    output_dir = args.destdir

# Create directories
include_output_dir = os.path.join(output_dir, 'include', 'AL')
src_output_dir = os.path.join(output_dir, 'src')
if not os.path.exists(include_output_dir):
    os.makedirs(include_output_dir)
if not os.path.exists(src_output_dir):
    os.makedirs(src_output_dir)

# Parse function names from alc.h, al.h and efx.h
procs = []
efxProcs = []

def parse_func_names(procs_, header, p):
    with open(header, 'r') as f:
        for line in f:
            m = p.match(line)
            if m:
                procs_.append(m.group(1))

print('Parsing alc.h header...')
parse_func_names(procs, 'include/AL/alc.h', re.compile(r'ALC_API.*ALC_APIENTRY\s+(\w+)'))

print('Parsing al.h header...')
parse_func_names(procs, 'include/AL/al.h', re.compile(r'AL_API.*AL_APIENTRY\s+(\w+)'))

print('Parsing efx.h header...')
parse_func_names(efxProcs, 'include/AL/efx.h', re.compile(r'AL_API.*AL_APIENTRY\s+(\w+)'))

procs.sort()
efxProcs.sort()

def proc_t(proc):
    return { 'p': proc,
             'p_s': 'alcw' + proc[3:] if proc[:3] == 'alc' else 'alw' + proc[2:],
             'p_t': 'LP' + proc.upper() }

# Generate alw.h
print('Generating alw.h in include/AL...')
with open(os.path.join(include_output_dir, 'alw.h'), 'wb') as f:
    f.write(UNLICENSE)
    f.write(br'''#ifndef __alw_h_
#define __alw_h_

#include <AL/alc.h>
#define AL_NO_PROTOTYPES
#include <AL/al.h>
#include <AL/efx.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*ALWalproc)(void);

/* alw api */
int alwInit(void);
int alwInitEfx(void);
void alwTerminate(void);

/* OpenAL functions */
''')
    for proc in procs:
        f.write('extern {0[p_t]: <52} {0[p_s]};\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(b'\n')
    for proc in procs:
        f.write('#define {0[p]: <45} {0[p_s]}\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''
/* Effects extension functions */
''')
    for proc in efxProcs:
        f.write('extern {0[p_t]: <52} {0[p_s]};\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(b'\n')
    for proc in efxProcs:
        f.write('#define {0[p]: <45} {0[p_s]}\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''
#ifdef __cplusplus
}
#endif

#endif
''')

# Generate alw.c
print('Generating alw.c in src...')
with open(os.path.join(src_output_dir, 'alw.c'), 'wb') as f:
    f.write(UNLICENSE)
    f.write(br'''#include <AL/alw.h>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN 1
#include <windows.h>

static HMODULE libal;

static int open_libal(void)
{
	libal = LoadLibraryA("openal32.dll");
	return libal != NULL;
}

static void close_libal(void)
{
	FreeLibrary(libal);
}

static void *get_proc(const char *proc)
{
	return GetProcAddress(libal, proc);
}
#elif defined(__APPLE__) || defined(__APPLE_CC__)
#include <Carbon/Carbon.h>

CFBundleRef bundle;
CFURLRef bundleURL;

static int open_libal(void)
{
	bundleURL = CFURLCreateWithFileSystemPath(kCFAllocatorDefault,
		CFSTR("/System/Library/Frameworks/OpenAL.framework"),
		kCFURLPOSIXPathStyle, true);

	bundle = CFBundleCreate(kCFAllocatorDefault, bundleURL);
	return bundle != NULL;
}

static void close_libal(void)
{
	CFRelease(bundle);
	CFRelease(bundleURL);
}

static void *get_proc(const char *proc)
{
	void *res;

	CFStringRef procname = CFStringCreateWithCString(kCFAllocatorDefault, proc,
		kCFStringEncodingASCII);
	res = CFBundleGetFunctionPointerForName(bundle, procname);
	CFRelease(procname);
	return res;
}
#else
#include <stddef.h>
#include <dlfcn.h>

static void *libal;

static int open_libal(void)
{
	libal = dlopen("libopenal.so.1", RTLD_LAZY | RTLD_GLOBAL);
	return libal != NULL;
}

static void close_libal(void)
{
	dlclose(libal);
}

static void *get_proc(const char *proc)
{
	return dlsym(libal, proc);
}
#endif

static void load_procs(void);

int alwInit(void)
{
	int res = open_libal();
	if (res) load_procs();
	return res ? 0 : -1;
}

static void load_efx_procs(void);

int alwInitEfx(void)
{
	if (!libal) return -1;
	load_efx_procs();
	return 0;
}

void alwTerminate(void)
{
	close_libal();
}

''')
    for proc in procs:
        f.write('{0[p_t]: <52} {0[p_s]};\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''
/* EFX entry points */
''')
    for proc in efxProcs:
        f.write('{0[p_t]: <52} {0[p_s]};\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''
static void load_procs(void)
{
''')
    for proc in procs:
        f.write('\t{0[p_s]} = ({0[p_t]}) get_proc("{0[p]}");\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(br'''}

static void load_efx_procs(void)
{
''')
    for proc in efxProcs:
        f.write('\t{0[p_s]} = ({0[p_t]}) alwGetProcAddress("{0[p]}");\n'.format(proc_t(proc)).encode("utf-8"))
    f.write(b'}\n')
