from __future__ import absolute_import
from __future__ import print_function

import io
import os.path
import codecs

from .visitors import (formatters as formattervisitors,
                       flatteners as flattenervisitors,
                       solvers as solvervisitors,
                       importers as importervisitors)
from . import parsers, defs, errors
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
    def __init__(self, stylesheet, importing_filename, import_directories, options=None):
        self.options = options or {}
        self.finders = []
        if self.options.get('curfile_relative_imports', 
                            defs.IMPORT_RELATIVE_TO_CURRENT_FILE):
            # look relative to directory of 'importing_filename'
            self.finders.append(FileRelativeFinder(importing_filename))
        if self.options.get('toplevel_relative_imports', 
                            defs.IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET):
            # look relative to top-level stylesheet directory
            toplevel_filename = os.path.abspath(stylesheet.filename)
            finder = FileRelativeFinder(os.path.dirname(toplevel_filename))
            self.finders.append(finder)
        finders = self.options.get('import_finders', None)
        if finders:
            self.finders.extend(finders)
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
        self.options = options or {}
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
        stylesheet = pw.parse_file(filename,
                                   source_encoding=self.source_encoding, 
                                   default_encoding=default_encoding)
        return stylesheet
        
    def on_import(self, filename, default_encoding, import_sequence):
        """Opens and parses an imported stylesheet.  This is called recursively 
        if an imported stylesheet contains imports of its own.
        """
        # TODO: filename must also meet other criteria to be eligible for import
        if filename:
            filename = self.resolve_filename(filename, import_sequence[-1])
            if not filename:
                # TODO: what happens if we can't resolve the filename
                raise RuntimeError()
            if filename in import_sequence:
                raise errors.CSSCircularImportError()
            
            stylesheet = self.parse(filename, default_encoding)
            import_sequence = import_sequence + (filename,)
            return self.do_imports(stylesheet, import_sequence)
        return None
        
    def do_imports(self, stylesheet, import_sequence):
        """Performs the imports on the stylesheet. This is called recursively 
        if imports are found.
        """
        def on_import(filename):
            return self.on_import(filename, stylesheet.encoding, import_sequence)
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
        self.options = options or {}
        self.reporter = reporter or reporters.NullReporter()
        default_encoding = default_encoding or defs.DEFAULT_ENCODING
        
        self.import_directories = import_directories or []
        self.Importer = Importer or self.DefaultImporter
        self.Parser = Parser or self.DefaultParser
        self.parser_wrapper = parsers.ParserWrapper(default_encoding=default_encoding, 
                                                    Parser=self.Parser)  # todo: pass options
                                            
        self.stylesheet = None
        
    def set_stylesheet(self, stylesheet):
        self.stylesheet = stylesheet
    
    def parse(self, file, filename=None, source_encoding=None, 
              default_encoding=None, do_decoding=True):
        # TODO: catch exceptions from parse()
        self.stylesheet = self.parser_wrapper.parse(file, filename=filename, 
                                            source_encoding=source_encoding, 
                                            default_encoding=default_encoding, 
                                            do_decoding=do_decoding)
        return self.stylesheet
    
    def parse_string(self, data, filename='<string>', source_encoding=None, 
                     default_encoding=None):
        # TODO: catch exceptions from parse_string()
        self.stylesheet = self.parser_wrapper.parse_string(data, 
                                            filename=filename, 
                                            source_encoding=source_encoding, 
                                            default_encoding=default_encoding)
        return self.stylesheet
        
    def process_imports(self):
        assert self.stylesheet
        if self.options.get('enable_imports', defs.ENABLE_IMPORTS):
            importer = self.Importer(self.stylesheet, self.import_directories, 
                                     options=self.options, 
                                     reporter=self.reporter)
            # TODO: catch exceptions from importer.run()
            importer.run()
        return self.stylesheet
        
    def apply_transforms(self):
        assert self.stylesheet
        enable_solve = self.options.get('enable_solve', defs.ENABLE_SOLVE)
        enable_flatten = self.options.get('enable_flatten', defs.ENABLE_FLATTEN)
        # TODO: catch exceptions from transforms
        if enable_solve:
            solver = solvervisitors.Solver(self.options)
            solver(self.stylesheet.rootnode)
        if enable_flatten and enable_solve:
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
        assert self.stylesheet
        stream = io.StringIO()
        writer = formattervisitors.CSSFormatterVisitor(stream)
        # TODO: catch exceptions from writer.visit()
        writer.visit(self.stylesheet.rootnode)
        return stream.getvalue()
        

#==============================================================================#        
