# The "Big" tests

import textwrap

from cssypy import core, errors

from . import base

#==============================================================================#
class SolverIntegration_TestCase(base.TestCaseBase):
    def test_variable_scopes1(self):
        src = u'''\
        $x: 8;
        s1 {
            $x: 5;
            r1: $x;
        }

        s2 {
            r2: $x;
        }
        '''
        expect = u'''\
        s1 {
            r1: 5;
        }
        s2 {
            r2: 8;
        }
        '''
        src = textwrap.dedent(src)
        expect = textwrap.dedent(expect)
        r = core.compile_string(src)
        self.assertEqual(expect, r)
    
    def test_variable_scopes2(self):
        src = u'''\
        s1 {
            $x: 5;
            r1: $x;
        }

        s2 {
            r2: $x;
        }
        '''
        src = textwrap.dedent(src)
        with self.assertRaises(errors.CSSVarNameError):
            core.compile_string(src)
            
    def test_variable_scopes3(self):
        src = u'''\
        s1 {
            $x: 6;
            r1: $x;
            s2 {
                $x: 7;
                r2: $x;
                s3 {
                    $x: 8;
                    r3: $x;
                    s4 {
                        $x: 9;
                        r4: $x;
                    }
                    r3a: $x;
                }
                r2a: $x;
            }
            r1a: $x;
        }
        '''
        expect = u'''\
        s1 {
            r1: 6;
            r1a: 6;
        }
        s1 s2 {
            r2: 7;
            r2a: 7;
        }
        s1 s2 s3 {
            r3: 8;
            r3a: 8;
        }
        s1 s2 s3 s4 {
            r4: 9;
        }
        '''
        src = textwrap.dedent(src)
        expect = textwrap.dedent(expect)
        r = core.compile_string(src)
        self.assertEqual(expect, r)

    def test_variable_expr1(self):
        src = u'''\
        $y: 8;
        s1 {
            $x: (5 + $y);
            r1: $x $y;
        }

        s2 {
            r2: (11 - $y);
            r3: ($y + $y);
        }
        '''
        expect = u'''\
        s1 {
            r1: 13 8;
        }
        s2 {
            r2: 3;
            r3: 16;
        }
        '''
        src = textwrap.dedent(src)
        expect = textwrap.dedent(expect)
        r = core.compile_string(src)
        self.assertEqual(expect, r)
        
    def test_nesting(self):
        src = u'''\
        $y: 8;
        s1 {
            $x: (5 + $y);
            r1: $x $y;
        }

        s2 {
            r2: (11 - $y);
            r3: ($y + $y);
        }
        '''
        expect = u'''\
        s1 {
            r1: 13 8;
        }
        s2 {
            r2: 3;
            r3: 16;
        }
        '''
        src = textwrap.dedent(src)
        expect = textwrap.dedent(expect)
        r = core.compile_string(src)
        self.assertEqual(expect, r)


