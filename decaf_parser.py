import sys
from decaf_lexer import *
from decaf_ast import *

field_record_counter = 1
constructor_record_counter = 1
method_record_counter = 7
variable_record_counter = 1
class_body_vars = []

precedence = (('right', 'ASSIGN'),
              ('left', 'OR'),
              ('left', 'AND'),
              ('nonassoc', 'EQ', 'NOT_EQ'),
              ('nonassoc', 'LT', 'LTE', 'GT', 'GTE'),
              ('left', 'PLUS', 'MINUS'),
              ('left', 'STAR', 'F_SLASH'),
              ('right', 'UMINUS', 'UPLUS', 'NOT')
              )

def p_program(p):
    'program : class_decl_list'

    # =======================================================================
    # Error Checking

    check_dup_classes(p[1]) # Check if two classes with the same name exist

    # Error Checking
    # =======================================================================

    # insert in and out classes
    p[1].insert(0, out_class)
    p[1].insert(0, in_class)

    p[0] = p[1]

def p_class_decl_list(p):
    '''class_decl_list : class_decl class_decl_list
                       | empty'''
    
    # if class_decl_list : class_decl class_decl_list
    if len(p) > 2:

        # =======================================================================
        # Error Checking

        # Check to see if the fields of the class to be appended has duplicate fields
        check_dup_fields(p[1].fields)
        
        # =======================================================================

        p[2].insert(0, p[1])
        p[0] = p[2]

    # if class_decl_list : empty
    else:
        p[0] = []

    pass

def p_class_decl(p):
    '''class_decl : CLASS ID LEFT_CB class_body_decl_list RIGHT_CB
                  | CLASS ID EXTENDS ID LEFT_CB class_body_decl_list RIGHT_CB'''

    new_class = class_record()
    new_class.class_name = p[2] # ID
    new_class.lineno = p.lineno(1)

    records = []

    # if class_decl : CLASS ID EXTENDS ID LEFT_CB class_body_decl_list RIGHT_CB
    if len(p) > 6:
        new_class.super_name = p[4] # ID
        records = p[6] # class_body_decl_list

    # if class_decl : CLASS ID LEFT_CB class_body_decl_list RIGHT_CB
    else:
        records = p[4] # class_body_decl_list

    # appends appropriate record
    for i in range(len(records)):
        
        # append field record (stored as lists)
        if type(records[i]) is list:
            for field in records[i]:
                field.containing_class = p[2] # ID
                new_class.fields.insert(0, field) 

        # append method record
        elif type(records[i]) is method_record:
            records[i].containing_class = p[2]
            new_class.methods.insert(0, records[i])

        # append constructor
        else:
            new_class.constructors.insert(0, records[i])

    p[0] = new_class
    pass

def p_class_body_decl_list(p):
    'class_body_decl_list : class_body_decl class_body_decl_cont'

    p[2].append(p[1])

    p[0] = p[2]
    pass

def p_class_body_decl_cont(p):
    '''class_body_decl_cont : class_body_decl class_body_decl_cont
                            | empty'''
    
    # class_body_decl_cont : empty
    if p[1] == None:
        p[0] = []

    # class_body_decl_cont : class_body_decl class_body_decl_cont
    else:
        p[2].append(p[1])
        p[0] = p[2]

    pass

def p_class_body_decl(p):
    '''class_body_decl : field_decl
                       | method_decl
                       | constructor_decl'''
    
    global variable_record_counter
    # reset variable_record_counter
    variable_record_counter = 1

    p[0] = p[1]
    pass

def p_field_decl(p):
    'field_decl : modifier var_decl'

    global field_record_counter
    
    # generates field record for each variable
    new_field_records = []
    variables = p[2]

    # take variables and make field records for each
    for i in range(len(variables)):
        new_field = field_record()
        new_field.field_name = variables[i].variable_name
        new_field.lineno = variables[i].lineno
        new_field.field_id = field_record_counter
        field_record_counter += 1
        # new_field.containing_class left for class_decl to decide
        modifier = p[1] # holds an array consisting of strings denoting visibility and/or applicability

        if len(modifier) == 1 :
            # STATIC
            if modifier[0] == "static":
                new_field.field_visibility = "private"
                new_field.field_applicability = modifier[0]

            # PUBLIC or PRIVATE or NONE
            else:
                new_field.field_visibility = modifier[0]
                new_field.field_applicability = "instance"
                # NONE ([None])
                if modifier[0] == None:
                    new_field.field_visibility = "private"

        # PUBLIC STATIC or PRIVATE STATIC
        elif len(modifier) == 2:
            new_field.field_visibility = modifier[0]
            new_field.field_applicability = modifier[1]

        new_field.type = variables[i].type
        new_field_records.append(new_field)

    p[0] = new_field_records
    pass

def p_modifier(p):
    '''modifier : PUBLIC STATIC
                | PRIVATE STATIC
                | PUBLIC
                | PRIVATE
                | STATIC
                | empty'''

    # Passes an array containing one or more modifiers.
    # If no modifier is given, it will pass an array containing only None.

    if(len(p) == 2):
        p[0] = [p[1]]

    else:
        p[0] = [p[1], p[2]]
        
    pass

def p_var_decl(p):
    'var_decl : type variables SEMI_COLON'

    current_variables = p[2] # variables

    # gives all variables a type
    for i in range(0,len(current_variables)):
        current_variables[i].type = p[1]
    
    p[0] = current_variables
    pass

def p_type(p):
    '''type : TYPE_INT
            | TYPE_FLOAT
            | TYPE_BOOLEAN
            | ID'''

    current_type = type_record()
    if str(p[1]) != "int" and str(p[1]) != "float" and str(p[1]) != "boolean" and str(p[1]) != "string":
        current_type.type = "user(" + str(p[1]) + ")"
    else:
        current_type.type = str(p[1])

    p[0] = current_type
    pass

def p_variables(p):
    'variables : variable variables_cont'

    p[2].insert(0, p[1])

    p[0] = p[2]
    pass

def p_variables_cont(p):
    '''variables_cont : COMMA variable variables_cont
                      | empty'''
    
    # variables_cont : COMMA variable variables_cont
    if(len(p) > 2):
        p[3].insert(0,p[2])
        p[0] = p[3]

    # variables_cont : empty
    else:
        p[0] = []

    pass

def p_variable(p):
    'variable : ID'
    
    global variable_record_counter
    variable = variable_record()
    variable.variable_name = p[1] # ID
    variable.lineno = p.lineno(1)
    variable.variable_kind = "local" # local unless changed to a formal parameter (refer to p_formal_param)
    variable.variable_id = variable_record_counter
    variable_record_counter += 1

    p[0] = variable
    pass

def p_method_decl(p):
    '''method_decl : modifier type ID LEFT_PN formals RIGHT_PN block
                   | modifier TYPE_VOID ID LEFT_PN formals RIGHT_PN block'''
    
    # =========================================
    # Error checking
    
    vars = []
    vars.extend(p[5]) # formals
    for statement in p[7].statements: # block.statements
        if isinstance(statement, var_decl_statement):
            vars.extend(statement.var_decls)
        else:
            break
    check_dup_vars(vars) 

    # Error checking
    # =========================================

    global method_record_counter

    new_method = method_record()
    new_method.method_name = p[3]
    new_method.method_id = method_record_counter
    new_method.method_parameters = p[5].copy() # formals
    new_method.method_body = p[7] # block
    method_record_counter += 1

    modifier = p[1] # holds an array consisting of strings denoting visibility and/or applicability        

    if len(modifier) == 1 :
        # STATIC
        if modifier[0] == "static":
            new_method.method_visibility = "private"
            new_method.method_applicability = modifier[0]

        # PUBLIC or PRIVATE or NONE
        else:
            new_method.method_visibility = modifier[0]
            new_method.method_applicability = "instance"
            # NONE
            if modifier[0] == None:
                new_method.method_visibility = "private"

    # PUBLIC STATIC or PRIVATE STATIC
    elif len(modifier) == 2:
        new_method.method_visibility = modifier[0]
        new_method.method_applicability = modifier[1]

    if type(p[2]) == str:
        void_return_type = type_record()
        void_return_type.type = "void"
        new_method.return_type = void_return_type
    else:
        new_method.return_type = p[2]

    # stores all method variables into their variable table
    global class_body_vars
    new_method.variable_table = p[5] # formals
    new_method.variable_table.extend(class_body_vars) # variables inside of method body
    class_body_vars = []
    
    p[0] = new_method

    pass

def p_constructor_decl(p):
    'constructor_decl : modifier ID LEFT_PN formals RIGHT_PN block'

    # =========================================
    # Error checking
    
    vars = []
    vars.extend(p[4]) # formals
    for statement in p[6].statements: # block.statements
        if isinstance(statement, var_decl_statement):
            vars.extend(statement.var_decls)
        else:
            break
    check_dup_vars(vars) 

    # Error checking
    # =========================================
    
    global constructor_record_counter

    cons_record = constructor_record()
    cons_record.constructor_id = constructor_record_counter
    cons_record.constructor_parameters = p[4].copy()
    cons_record.variable_table = p[4] # formals
    cons_record.constructor_body = p[6] # constructor body
    
    # append statement variables into variable table
    global class_body_vars
    cons_record.variable_table.extend(class_body_vars) # variables inside of constructor body
    class_body_vars = []

    modifier = p[1] # modifier
    if modifier[0] == None or modifier[0] == "static":
        cons_record.constructor_visibility = "private"
    else:
        cons_record.constructor_visibility = modifier[0]

    constructor_record_counter += 1

    p[0] = cons_record
    pass

# Passes an array of variables OR an empty array
def p_formals(p):
    '''formals : formal_param formals_cont
               | empty'''

    # MUST RETURN AN ARRAY (refer to p_method_decl)

    formal_params = []

    # formals : formal_param formals_cont
    if(len(p) > 2):
        p[2].insert(0, p[1])
        formal_params = p[2]

    p[0] = formal_params
    pass

# Passes on the array of variables with the newest variable parsed added to it
def p_formals_cont(p):
    '''formals_cont : COMMA formal_param formals_cont
                    | empty'''

    # formals_cont : COMMA formal_param formals_cont
    if(len(p) > 2):
        p[3].insert(0, p[2])
        p[0] = p[3]

    # formals_cont : empty
    else:
        p[0] = []
    
    pass

# Passes on the variable record while setting its type
def p_formal_param(p):
    'formal_param : type variable'

    p[2].type = p[1] # type
    p[2].variable_kind = "formal" # kind

    p[0] = p[2]
    pass

def p_block(p):
    'block : LEFT_CB stmt_list RIGHT_CB'
    
    # =========================================
    # Error checking

    vars = []
    for stmt in p[2]:
        if isinstance(stmt, var_decl_statement):
            vars.extend(stmt.var_decls)
        else:
            break
    check_dup_vars(vars) 

    # Error checking
    # =========================================

    block = block_statement()
    block.statements = p[2] # stmt_list

    p[0] = block
    pass

def p_stmt_list(p):
    '''stmt_list : stmt stmt_list
                 | empty'''

    # stmt_list : stmt stmt_list
    if len(p) > 2:
        p[2].insert(0,p[1])
        p[0] = p[2]

    # stmt_list : empty
    else:
        p[0] = []

    pass

def p_stmt(p):
    '''stmt : IF LEFT_PN expr RIGHT_PN stmt 
            | IF LEFT_PN expr RIGHT_PN stmt ELSE stmt
            | WHILE LEFT_PN expr RIGHT_PN stmt
            | FOR LEFT_PN for_cond1 SEMI_COLON for_cond2 SEMI_COLON for_cond3 RIGHT_PN stmt
            | RETURN return_val SEMI_COLON
            | stmt_expr SEMI_COLON
            | BREAK SEMI_COLON
            | CONTINUE SEMI_COLON
            | block
            | var_decl
            | SEMI_COLON'''
    
    statement = None
    if str(p[1]) == "if":
        statement = if_statement()
        statement.if_cond = p[3] # expr
        statement.then_part = p[5] # stmt

        skip_stmt = skip_statement()
        statement.else_part = skip_stmt
        
        # if else statement
        if len(p) > 6:
            statement.else_part = p[7] # stmt
    
    elif str(p[1]) == "while":
        statement = while_statement()
        statement.loop_cond = p[3] # expr
        statement.loop_body = p[5] # stmt
    
    elif str(p[1]) == "for":
        statement = for_statement()
        statement.initializer = p[3] # for_cond1
        statement.loop_cond = p[5] # for_cond2
        statement.update_expr = p[7] # for_cond3
        statement.loop_body = p[9] # stmt
    
    elif str(p[1]) == "return":
        statement = return_statement()
        statement.return_value = p[2] # return_val
        statement.line_range = p.linespan(1) # linespan

    elif str(p[1]) == "break":
        statement = break_statement()
    
    elif str(p[1]) == "continue":
        statement = continue_statement()

    elif str(p[1]) == ";":
        statement = skip_statement()
    
    # block
    elif isinstance(p[1], block_statement):
        statement = p[1]

    # stmt expr
    elif isinstance(p[1], expression_record):
        statement = expression_statement()
        statement.expression = p[1] # stmt_expr
    
    # variable declaration
    elif type(p[1]) == list:

        statement = var_decl_statement()

        for variable in p[1]:
            
            statement.var_decls.append(variable)
            class_body_vars.append(variable)

    p[0] = statement
    pass

def p_for_cond1(p):
    '''for_cond1 : stmt_expr
                 | empty'''

    new_expression = expression_statement()
    new_expression.expression = p[1]

    if p[1] == None:
        p[0] = None
    else:
        p[0] = new_expression

    pass

def p_for_cond2(p):
    '''for_cond2 : expr
                 | empty'''
    
    
    p[0] = p[1]
    pass

def p_for_cond3(p):
    '''for_cond3 : stmt_expr
                 | empty'''
    
    new_expression = expression_statement()
    new_expression.expression = p[1]

    if p[1] == None:
        p[0] = None
    else:
        p[0] = new_expression

    pass

def p_return_val(p):
    '''return_val : expr
                  | empty'''
    
    p[0] = p[1]
    pass

def p_literal(p):
    '''literal : INT_CONST
               | FLOAT_CONST
               | STRING_CONST
               | NULL
               | TRUE
               | FALSE'''

    new_expression = constant_expression()
    new_expression.value = p[1]

    p[0] = new_expression
    pass

def p_primary(p):
    '''primary : literal
               | THIS
               | SUPER
               | LEFT_PN expr RIGHT_PN
               | NEW ID LEFT_PN arguments RIGHT_PN
               | lhs
               | method_invocation'''

    # primary : NEW ID LEFT_PN arguments RIGHT_PN
    if p[1] == "new":
        curr_expression = new_object_expression()
        curr_expression.base = p[2] # ID
        curr_expression.arguments = p[4] # arguments
        p[0] = curr_expression

    # primary : THIS
    elif p[1] == "this":
        p[0] = this_expression()

    # primary : SUPER
    elif p[1] == "super":
        p[0] = super_expression()

    # primary : LEFT_PN expr RIGHT_PN
    elif p[1] == "(":
        p[0] = p[2] # expr

    # Runs in the case of either literal, lhs, or method_invocation, which are all expressions anyways and should be passed up for parent functions to decide what to do with them
    else:
        p[0] = p[1]

    pass

def p_arguments(p):
    '''arguments : expr arguments_cont
                 | empty'''
    
    # arguments : expr arguments_cont
    if len(p) > 2:
       p[2].append(p[1])
       p[0] = p[2]

    # arguments : empty
    else:
       p[0] = []
    
    pass

def p_arguments_cont(p):
    '''arguments_cont : COMMA expr arguments_cont
                      | empty'''
    
    # arguments_cont : COMMA expr arguments_cont
    if len(p) > 2:
        p[3].append(p[2])
        p[0] = p[3]

    # arguments_cont : empty
    else:
        p[0] = []

    pass

def p_lhs(p):
    'lhs : field_access'

    p[0] = p[1]
    pass

def p_field_access(p):
    '''field_access : primary DOT ID
                    | ID'''
    
    new_expression = None
    if len(p) > 2:
        new_expression = field_access_expression()
        new_expression.base = p[1] # primary
        new_expression.field_name = p[3] # ID

    else:
        new_expression = var_expression()
        new_expression.name = p[1]
        new_expression.id = -1
        
    p[0] = new_expression
    pass

def p_method_invocation(p):
    'method_invocation : field_access LEFT_PN arguments RIGHT_PN'

    # NOTE: field_access MUST be a field_access_expression

    new_expression = method_call_expression()
    new_expression.base = p[1].base # Gets base member from field record in p[1] (always be primary DOT ID)
    new_expression.method_name = p[1].field_name # Gets field_name member from field record in p[1]
    new_expression.arguments = p[3]
    
    p[0] = new_expression
    pass

def p_expr(p):
    '''expr : primary
            | assign'''
    
    p[0] = p[1]
    pass

def p_assign(p):
    '''assign : lhs ASSIGN expr
              | lhs INCREMENT
              | INCREMENT lhs
              | lhs DECREMENT
              | DECREMENT lhs'''

    new_expression = None
    if p[2] == "=":
        new_expression = assign_expression()
        new_expression.lhs = p[1] # lhs (field_access)
        new_expression.rhs = p[3] # expr

    else:
        new_expression = auto_expression()

        # prefix
        if p[1] == "++" or p[1] == "--": 
            new_expression.operand = p[2]
            new_expression.fix = "pre"
            if p[1] == "++":
                new_expression.auto = "inc"
            else:
                new_expression.auto = "dec"

        # postfix
        else:
            new_expression.operand = p[1]
            new_expression.fix = "post"
            if p[2] == "++":
                new_expression.auto = "inc"
            else:
                new_expression.auto = "dec"

    p[0] = new_expression
    pass

def p_add_expr(p):
    'expr : expr PLUS expr'

    p[0] = binary_expression(p[1], p[3], "add")
    pass

def p_sub_expr(p):
    'expr : expr MINUS expr'

    p[0] = binary_expression(p[1], p[3], "sub")
    pass

def p_mult_exp(p):
    'expr : expr STAR expr'

    p[0] = binary_expression(p[1], p[3], "mul")
    pass

def p_div_expr(p):
    'expr : expr F_SLASH expr'

    p[0] = binary_expression(p[1], p[3], "div")
    pass

def p_conj_expr(p):
    'expr : expr AND expr'

    p[0] = binary_expression(p[1], p[3], "and")
    pass

def p_disj_expr(p):
    'expr : expr OR expr'

    p[0] = binary_expression(p[1], p[3], "or")
    pass

def p_equals_expr(p):
    'expr : expr EQ expr'

    p[0] = binary_expression(p[1], p[3], "eq")
    pass

def p_notequals_expr(p):
    'expr : expr NOT_EQ expr'

    p[0] = binary_expression(p[1], p[3], "neq")
    pass

def p_lt_expr(p):
    'expr : expr LT expr'

    p[0] = binary_expression(p[1], p[3], "lt")
    pass

def p_lte_expr(p):
    'expr : expr LTE expr'

    p[0] = binary_expression(p[1], p[3], "leq")
    pass

def p_gt_expr(p):
    'expr : expr GT expr'

    p[0] = binary_expression(p[1], p[3], "gt")
    pass

def p_gte_expr(p):
    'expr : expr GTE expr'

    p[0] = binary_expression(p[1], p[3], "geq")
    pass

def p_pos_expr(p):
    'expr : PLUS expr %prec UPLUS'

    p[0] = p[2]
    pass

def p_minus_expr(p):
    'expr : MINUS expr %prec UMINUS'

    new_expression = unary_expression()
    new_expression.operand = p[2] # expr
    new_expression.operator = "uminus"

    p[0] = new_expression
    pass

def p_not_expr(p):
    'expr : NOT expr'
    
    new_expression = unary_expression()
    new_expression.operand = p[2] # expr
    new_expression.operator = "neg"

    p[0] = new_expression
    pass

def p_stmt_expr(p):
    '''stmt_expr : assign
                 | method_invocation'''

    p[0] = p[1]
    pass

def p_newline(p):
    '''newline : '''

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    print()
    if p:
        print("Syntax error at token,", p.type, ", line", p.lineno)
    else:
        print("Syntax error at EOF")
    print()
    sys.exit()

# ==================================================================
# Error checking functions

# given a list of variables, check to see if there are any duplicate variables among them
def check_dup_vars(vars):
    for i in range(0, len(vars)):
        for j in range(i+1, len(vars)):
            if vars[i].variable_name == vars[j].variable_name:
                raise Exception("Two variables have the same name! (LINE " + str(vars[j].lineno) + ")")

def check_dup_fields(fields):
    for i in range(0, len(fields)): 
        for j in range(i+1, len(fields)):
            if(fields[i].field_name == fields[j].field_name):
                raise Exception("Two fields have the same name! (LINE " + str(fields[j].lineno) + ")")
                    
def check_dup_classes(classes):
    for i in range(len(classes)):
        for j in range(i+1, len(classes)):
            if(classes[i].class_name == classes[j].class_name):
                raise Exception("Two classes have the same name! (LINE " + str(classes[j].lineno) + ")")

# Error checking functions
# ==================================================================

# ==================================================================
# In and Out classes

# In Class
in_class = class_record("In")

# scan_int method
in_class.methods.append(method_record("scan_int", 1, "In", "public", "static", [], type_record("int")))

# scan_float method
in_class.methods.append(method_record("scan_float", 2, "In", "public", "static", [], type_record("float")))

# Out Class
out_class = class_record("Out")
print_int = method_record("print", 3, "Out", "public", "static", [variable_record("i", 1, "formal", type_record("int"))], type_record("void"), [variable_record("i", 1, "formal", type_record("int"))])
print_float = method_record("print", 4, "Out", "public", "static", [variable_record("f", 1, "formal", type_record("float"))], type_record("void"), [variable_record("f", 1, "formal", type_record("float"))])
print_boolean = method_record("print", 5, "Out", "public", "static", [variable_record("b", 1, "formal", type_record("boolean"))], type_record("void"), [variable_record("s", 1, "formal", type_record("boolean"))])
print_string = method_record("print", 6, "Out", "public", "static", [variable_record("s", 1, "formal", type_record("string"))], type_record("void"), [variable_record("b", 1, "formal", type_record("string"))])

out_class.methods.append(print_int)
out_class.methods.append(print_float)
out_class.methods.append(print_boolean)
out_class.methods.append(print_string)

# In and Out classes
# ==================================================================