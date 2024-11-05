import sys
import ply.lex as lex
import ply.yacc as yacc
from decaf_parser import *
from decaf_ast import *
from decaf_typecheck import *

def just_scan():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    import decaf_lexer
    lexer = lex.lex(module = decaf_lexer, debug = 0)

    fh = open(fn, 'r')
    source = fh.read()
    lexer.input(source)
    next_token = lexer.token()
    while next_token != None:
        #print(next_token)
        next_token = lexer.token()
# end def just_scan()


def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    import decaf_lexer
    import decaf_parser
    lexer = lex.lex(module = decaf_lexer, debug = 0)
    parser = yacc.yacc(module = decaf_parser, debug = 0)

    fh = open(fn, 'r')
    source = fh.read()
    fh.close()
    result = parser.parse(source, lexer = lexer, debug = 0)
    
    # ==================================================================
    # Scope resolution

    for i in range(2, len(result)):

        # Resolve the variables inside of a constructor
        for j in range(len(result[i].constructors)):
            # Create a new copy of the current method's parameters
            curr_constructor_parameters = []
            curr_constructor_parameters.extend(result[i].constructors[j].constructor_parameters)
            resolve_statement_vars(result[i].constructors[j].constructor_body.statements, result, curr_constructor_parameters)

        for k in range(len(result[i].methods)):
            # Create a new copy of the current method's parameters
            curr_method_parameters = []
            curr_method_parameters.extend(result[i].methods[k].method_parameters)
            resolve_statement_vars(result[i].methods[k].method_body.statements, result, curr_method_parameters)

    # Scope resolution
    # ==================================================================

    # Parsing Successful
    #print()
    print("YES")
    #print()
    #check_class_table()
    type_check(result)
    #print_class_table(result)

# ==================================================================
# Scope resolution helper functions

def resolve_statement_vars(statements, classes, valid_vars):

    """
    Resolves the variable IDs inside of an array of statements.

    Parameters
    ----------
    statements : list
        The list of statement records
    curr_class : class_record
        The class record that the statements belong to
    valid_vars : list
        The list of variables that are valid within the current block

    Returns
    -------
    void
    """

    new_valid_vars = []
    new_valid_vars.extend(valid_vars)

    for i in range(len(statements)):

        if isinstance(statements[i], if_statement):
            resolve_expression_vars(statements[i].if_cond, classes, new_valid_vars)
            if type(statements[i].if_cond) != block_statement:
                resolve_statement_vars([statements[i].then_part], classes, new_valid_vars)
            else:
                resolve_statement_vars(statements[i].then_part.statements, classes, new_valid_vars)
            if not isinstance(statements[i].else_part, skip_statement):
                if type(statements[i].if_cond) != block_statement:
                    resolve_statement_vars([statements[i].else_part], classes, new_valid_vars)
                else:
                    resolve_statement_vars(statements[i].else_part.statements, classes, new_valid_vars)

        elif isinstance(statements[i], while_statement):
            resolve_expression_vars(statements[i].loop_cond, classes, new_valid_vars)
            resolve_statement_vars(statements[i].loop_body.statements, classes, new_valid_vars)

        elif isinstance(statements[i], for_statement):
            resolve_statement_vars([statements[i].initializer], classes, new_valid_vars)
            resolve_expression_vars(statements[i].loop_cond, classes, new_valid_vars)
            resolve_statement_vars([statements[i].update_expr], classes, new_valid_vars)
            resolve_statement_vars(statements[i].loop_body.statements, classes, new_valid_vars)

        elif isinstance(statements[i], return_statement):
            resolve_expression_vars(statements[i].return_value, classes, new_valid_vars)

        elif isinstance(statements[i], expression_statement):
            resolve_expression_vars(statements[i].expression, classes, new_valid_vars)

        elif isinstance(statements[i], block_statement):
            resolve_statement_vars(statements[i].statements, classes, new_valid_vars)

        elif isinstance(statements[i], var_decl_statement):
            new_valid_vars.extend(statements[i].var_decls)

def resolve_expression_vars(expression, classes, valid_vars):

    """
    Resolves the variable IDs inside of an expression.

    Parameters
    ----------
    expression : expression_record
        The given expression
    curr_class : class_record
        A list of valid class records
    valid_variables : list
        A list of variable records that are valid within the expression

    Returns
    -------
    void
    """
    new_valid_vars = []
    new_valid_vars.extend(valid_vars)

    if isinstance(expression, var_expression):
        return find_variable(expression, classes, new_valid_vars) 

    elif isinstance(expression, unary_expression):
        resolve_expression_vars(expression.operand, classes, new_valid_vars)
        
    elif isinstance(expression, binary_expression):
        resolve_expression_vars(expression.fst_operand, classes, new_valid_vars)
        resolve_expression_vars(expression.snd_operand, classes, new_valid_vars)
    
    elif isinstance(expression, assign_expression):
       resolve_expression_vars(expression.lhs, classes, new_valid_vars)
       resolve_expression_vars(expression.rhs, classes, new_valid_vars)
    
    elif isinstance(expression, auto_expression):
       resolve_expression_vars(expression.operand, classes, new_valid_vars)
    
    elif isinstance(expression, field_access_expression):
        if resolve_expression_vars(expression.base, classes, new_valid_vars) == 1:
            expression.base = class_reference_expression(expression.base.name)
           
    elif isinstance(expression, method_call_expression):
       if resolve_expression_vars(expression.base, classes, new_valid_vars) == 1:
            expression.base = class_reference_expression(expression.base.name)
       for i in range(len(expression.arguments)):
           resolve_expression_vars(expression.arguments[i], classes, new_valid_vars)
    
    elif isinstance(expression, new_object_expression):
        for i in range(len(expression.arguments)):
            resolve_expression_vars(expression.arguments[i], classes, new_valid_vars)
    
def find_variable(var, classes, valid_vars):
    """
    Assigns the ID of a variable to an associated variable record's ID.
    If the variable record isn't found, then the function will check if
    an associated class reference has been found instead.

    Parameters
    ----------
    expression : expression_record
        The given expression
    curr_class : class_record
        A list of valid class records
    valid_variables : list
        A list of variable records that are valid within the expression

    Returns
    -------
    0 if the given variable expression ID has been assigned an associated variable record ID.
    1 otherwise if an associated class reference has been found.

    Raises
    -------
    Error if neither a variable record nor a class reference was found.
    """

    for curr_var_record in reversed(valid_vars):
        if var.name == curr_var_record.variable_name:
            var.id = curr_var_record.variable_id
            return 0

    # Variable record wasn't found, so look a matching class name
    for curr_class in classes:
        if var.name == curr_class.class_name:
            return 1
            
    raise Exception("Variable name not found in current scope and classes!")

# Scope resolution helper functions
# ==================================================================

if __name__ == "__main__":
    just_scan()
    main()