from __future__ import absolute_import
from __future__ import print_function

import sys

import six

from . import processors, parsers, optionsdict

#==============================================================================#
def compile_string(src, source_encoding=None, dest_encoding=None, 
                   default_encoding=None, import_directories=None, 
                   options=None, reporter=None):
    options = options or {}
    if isinstance(options, dict):
        options.setdefault('ENABLE_SOLVE', True)
        options.setdefault('ENABLE_IMPORTS', True)
        options.setdefault('PROPAGATE_EXCEPTIONS', True)
    else:
        raise RuntimeError() # TODO
    
    options = optionsdict.Options(options)
    proc = processors.Processor(default_encoding=default_encoding, 
                                import_directories=import_directories, 
                                options=options, reporter=reporter)
    proc.parse_string(src, source_encoding=source_encoding)
    proc.process_imports()
    proc.apply_transforms()
    return proc.write_string()

#==============================================================================#
def compile(ifile, ofile, ifilename=None, ofilename=None, source_encoding=None, 
            dest_encoding=None, default_encoding=None, import_directories=None, 
            options=None, reporter=None):
    
    stream_in = stream_out = False
    
    # Special handling for the two cases where we read from a stream.
    if ifile == '-':        # pragma: no cover
        stream_in = True
        ifile = sys.stdin
        ifilename = sys.stdin.name
    elif not isinstance(ifile, six.string_types):
        stream_in = True
    
    # Special handling for the two cases where we write to a stream.
    if ofile == '-':        # pragma: no cover
        stream_out = True
        ofile = sys.stdout
        ofilename = sys.stdout.name
    elif not isinstance(ofile, six.string_types):
        stream_out = True
    
    # Build the processor and parse the input.
    proc = processors.Processor(default_encoding=default_encoding, 
                                import_directories=import_directories, 
                                options=options, reporter=reporter)
    proc.parse(ifile, filename=ifilename, source_encoding=source_encoding)
    
    # Do transforms.
    proc.process_imports()
    proc.apply_transforms()
    
    # Write the result.
    if stream_out:
        proc.write_stream(ofile, filename=ofilename, encoding=dest_encoding)
    else:
        proc.write(ofile, encoding=dest_encoding)

#==============================================================================#

