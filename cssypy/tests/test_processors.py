import os.path

from cssypy import processors, parsers, optionsdict, errors, nodes

from . import base

class Importer_TestCase(base.TestCaseBase):
    def test_recursive1(self):
        filename = os.path.join(self.DATAPATH, 'recursive_imports', 'parent.css')
        import_directories = []
        opts = {'PROPAGATE_EXCEPTIONS': True}
        opts = optionsdict.Options(opts)
        
        parser = parsers.ParserWrapper(parsers.Parser)
        stylesheet = parser.parse_file(filename)
        
        importer = processors.Importer(stylesheet, import_directories, 
                                       options=opts)
        with self.assertRaises(errors.CSSCircularImportError) as cm:
            importer.run()
    
    def test_recursive2(self):
        # self-recursive
        filename = os.path.join(self.DATAPATH, 'recursive_imports', 'self_recursive.css')
        import_directories = []
        opts = {'PROPAGATE_EXCEPTIONS': True}
        opts = optionsdict.Options(opts)
        
        parser = parsers.ParserWrapper(parsers.Parser)
        stylesheet = parser.parse_file(filename)
        
        importer = processors.Importer(stylesheet, import_directories, 
                                       options=opts)
        with self.assertRaises(errors.CSSCircularImportError) as cm:
            importer.run()
            
    def test_import_not_found(self):
        filename = os.path.join(self.DATAPATH, 'imports', 'import_not_found.css')
        import_directories = []
        opts = {'PROPAGATE_EXCEPTIONS': True}
        opts = optionsdict.Options(opts)
        
        parser = parsers.ParserWrapper(parsers.Parser)
        stylesheet = parser.parse_file(filename)
        
        importer = processors.Importer(stylesheet, import_directories, 
                                       options=opts)
        rootnode = importer.run()
        
        self.assertEqual(1, len(rootnode.imports))
        self.assertTrue(isinstance(rootnode.imports[0], nodes.Import))
        self.assertEqual(u'this_stylesheet_does_not_exist.css', 
                         rootnode.imports[0].uri.string)
        

