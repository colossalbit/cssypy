from __future__ import absolute_import
from __future__ import print_function

import io
import os.path
import codecs
import sys

from .visitors import (formatters as formattervisitors,
                       flatteners as flattenervisitors,
                       solvers as solvervisitors,
                       importers as importervisitors)
from . import parsers, defs, errors, optionsdict
from .utils import reporters, stringutil

#==============================================================================#
stringutil.register_unicode_handlers()

#==============================================================================#
class FileRelativeFinder(object):
    def __init__(self, basefilepath):
        self.basefilepath = basefilepath  # relative to this file
        
    def find(self, filename):
        dir = os.path.dirname(self.basefilepath)
        filepath = os.path.join(dir, filename)
        if os.path.exists(filepath):
            assert os.path.isabs(filepath)
            return filepath
        return None
        
        
class DirectoryListFinder(object):
    def __init__(self, dirs):
        self.dirs = dirs
        
    def find(self, filename):
        filepaths = [os.path.join(dir, filename) for dir in self.dirs]
        for filepath in filepaths:
            if os.path.exists(filepath):
                assert os.path.isabs(filepath)
                return filepath
        return None


class ImportResolver(object):
    def __init__(self, stylesheet, importing_filename, import_directories, 
                 options=None):
        self.options = options or optionsdict.Options()
        assert isinstance(self.options, optionsdict.Options)
        self.finders = []
        
        if self.options.IMPORT_RELATIVE_TO_CURRENT_FILE:
            # look relative to directory of 'importing_filename'
            self.finders.append(FileRelativeFinder(importing_filename))
            
        if self.options.IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET:
            # look relative to top-level stylesheet directory
            toplevel_filename = os.path.abspath(stylesheet.filename)
            finder = FileRelativeFinder(os.path.dirname(toplevel_filename))
            self.finders.append(finder)
            
        self.finders.extend(finder() for finder in self.options.IMPORT_FINDERS)
        self.finders.append(DirectoryListFinder(import_directories))
        
    def resolve(self, filename):
        for finder in self.finders:
            filepath = finder.find(filename)
            if filepath:
                return filepath
        return None
    

class Importer(object):
    def __init__(self, stylesheet, import_directories, options=None, 
                 reporter=None):
        # 'import_directories' must contain absolute paths
        self.options = options or optionsdict.Options()
        assert isinstance(self.options, optionsdict.Options)
        self.reporter = reporter or reporters.NullReporter()
        if stylesheet.forced_encoding:
            self.source_encoding = stylesheet.encoding
        else:
            self.source_encoding = None
        self.Parser = stylesheet.Parser
        self.stylesheet = stylesheet
        self.import_directories = import_directories
        
    def resolve_filename(self, filename, importing_filename):
        assert os.path.isabs(importing_filename)
        resolver = ImportResolver(self.stylesheet, importing_filename, 
                                  self.import_directories, options=self.options)
        return resolver.resolve(filename)
        
    def parse(self, filename, default_encoding):
        pw = parsers.ParserWrapper(default_encoding=default_encoding, 
                                   Parser=self.Parser)
        try:
            stylesheet = pw.parse_file(filename,
                                       source_encoding=self.source_encoding, 
                                       default_encoding=default_encoding)
        except errors.CSSSyntaxError:
            if self.options.STOP_ON_IMPORT_SYNTAX_ERROR:
                raise
            return None
        return stylesheet
        
    def on_import(self, filename, default_encoding, import_sequence):
        """Opens and parses an imported stylesheet.  This is called recursively 
        if an imported stylesheet contains imports of its own.
        """
        if filename:
            filepath = self.resolve_filename(filename, import_sequence[-1])
            
            if not filepath:
                msg = "Unable to import stylesheet. File not found: '{}'"
                self.reporter.debug(msg.format(filename))
                if self.options.STOP_ON_IMPORT_NOT_FOUND:
                    sys.exit(1)
                return None
                
            if filepath in import_sequence:
                msg = "Stylesheet directly or indirectly imported itself: '{}'"
                raise errors.CSSCircularImportError(msg.format(filename))
            
            stylesheet = self.parse(filepath, default_encoding)
            import_sequence = import_sequence + (filepath,)
            if stylesheet:
                return self.do_imports(stylesheet, import_sequence)
            else:
                return None
        return None
        
    def do_imports(self, stylesheet, import_sequence):
        """Performs the imports on the stylesheet. This is called recursively 
        if imports are found.
        """
        def on_import(filename):
            return self.on_import(filename, stylesheet.encoding, 
                                  import_sequence)
        importer = importervisitors.Importer(callback=on_import)
        node = importer(stylesheet.rootnode)
        return node
        
    def run(self):
        import_sequence = (os.path.abspath(self.stylesheet.filename),)
        return self.do_imports(self.stylesheet, import_sequence)


#==============================================================================#
class Processor(object):
    DefaultImporter = Importer
    DefaultParser = parsers.Parser
    
    def __init__(self, default_encoding=None, Importer=None, Parser=None, 
                 import_directories=None, options=None, reporter=None):
        if isinstance(options, dict):
            options = optionsdict.Options(options)
        self.options = options or optionsdict.Options()
        assert isinstance(self.options, optionsdict.Options)
        
        self.reporter = reporter or reporters.NullReporter()
        default_encoding = default_encoding or defs.DEFAULT_ENCODING
        
        self.import_directories = import_directories or []
        self.Importer = Importer or self.DefaultImporter
        self.Parser = Parser or self.DefaultParser
        self.parser_wrapper = parsers.ParserWrapper(
                                            default_encoding=default_encoding, 
                                            Parser=self.Parser)  # todo: pass options
        
        self.stylesheet = None
        
    def set_stylesheet(self, stylesheet):
        self.stylesheet = stylesheet
        
    def on_syntax_error(self, e):
        if self.options.PROPAGATE_EXCEPTIONS:
            raise
        else:
            self.reporter.on_syntax_error(e)
            sys.exit(1)
    
    def parse(self, file, filename=None, source_encoding=None, 
              default_encoding=None, do_decoding=True):
        try:
            self.stylesheet = self.parser_wrapper.parse(file, filename=filename, 
                                            source_encoding=source_encoding, 
                                            default_encoding=default_encoding, 
                                            do_decoding=do_decoding)
        except errors.CSSSyntaxError as e:
            self.on_syntax_error(e)
        # TODO: catch other exceptions from wrapper.parse()
        return self.stylesheet
    
    def parse_string(self, data, filename='<string>', source_encoding=None, 
                     default_encoding=None):
        """Parse a string as a stylesheet. The string must be a unicode string. 
        The encoding arguments are not used to decode the string (as it is 
        already unicode).
        """
        try:
            self.stylesheet = self.parser_wrapper.parse_string(data, 
                                            filename=filename, 
                                            source_encoding=source_encoding, 
                                            default_encoding=default_encoding)
        except errors.CSSSyntaxError as e:
            self.on_syntax_error(e)
        # TODO: catch other exceptions from wrapper.parse_string()
        return self.stylesheet
        
    def process_imports(self):
        assert self.stylesheet
        if self.options.ENABLE_IMPORTS:
            importer = self.Importer(self.stylesheet, self.import_directories, 
                                     options=self.options, 
                                     reporter=self.reporter)
            try:
                importer.run()
            except CSSSyntaxError as e:
                self.on_syntax_error(e)
            # TODO: catch other exceptions from importer.run()
        return self.stylesheet
        
    def apply_transforms(self):
        assert self.stylesheet
        # TODO: catch exceptions from transforms
        
        if self.options.ENABLE_SOLVE:
            solver = solvervisitors.Solver(self.options)
            solver(self.stylesheet.rootnode)
            
        if self.options.ENABLE_FLATTEN and self.options.ENABLE_SOLVE:
            flattener = flattenervisitors.RulesetFlattener(self.options)
            flattener(self.stylesheet.rootnode)
        
        return self.stylesheet
        
    def write(self, filename, encoding=None):
        assert self.stylesheet
        encoding = encoding or self.stylesheet.encoding
        with io.open(filename, 'w', encoding=encoding, errors='cssypy') as stream:
            writer = formattervisitors.CSSFormatterVisitor(stream)
            # TODO: catch exceptions from writer.visit()
            writer.visit(self.stylesheet.rootnode)
        
    def write_stream(self, stream, filename=None, encoding=None):
        assert self.stylesheet
        encoding = encoding or self.stylesheet.encoding
        Stream = codecs.getwriter(encoding)
        stream = Stream(stream, errors='cssypy')
        writer = formattervisitors.CSSFormatterVisitor(stream)
        # TODO: catch exceptions from writer.visit()
        writer.visit(self.stylesheet.rootnode)
    
    def write_string(self):
        """Write the processed stylesheet to a unicode string."""
        assert self.stylesheet
        stream = io.StringIO()
        writer = formattervisitors.CSSFormatterVisitor(stream)
        # TODO: catch exceptions from writer.visit()
        writer.visit(self.stylesheet.rootnode)
        return stream.getvalue()
        

#==============================================================================#        
