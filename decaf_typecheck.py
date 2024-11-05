from decaf_ast import *
import re

# singleton smile
class TypeCheckerManager:
    def __init__(self, class_table):
        self.class_table = class_table # the given class table
        self.curr_class_index = 0 # the index of the current class that is being type checked in the table
        self.curr_class_body_decl = None # the current class body decl

def type_check(c_table):
    class_table = c_table
    
    if len(class_table) <= 2:
        return
    
    manager = TypeCheckerManager(c_table)

    for record in class_table:
        type_check_class(record, manager)
        manager.curr_class_index += 1

def type_check_class(c, manager):      
    for constructor in c.constructors:
        manager.curr_class_body_decl = constructor
        type_check_constructor(constructor, manager)

    for method in c.methods:
        manager.curr_class_body_decl = method
        type_check_method(method, manager)

def type_check_constructor(constructor, manager):
    type_check_statement(constructor.constructor_body, manager)

def type_check_method(method, manager):
    type_check_statement(method.method_body, manager)

# =========================================
# statement

def type_check_statement(statement, manager):
    if statement == None:
        return
    
    if type(statement) == if_statement:
        type_check_if_statement(statement, manager)
    if type(statement) == while_statement:
        type_check_while_statement(statement, manager)
    if type(statement) == for_statement:
        type_check_for_statement(statement, manager)
    if type(statement) == return_statement:
        type_check_return_statement(statement, manager)
    if type(statement) == expression_statement:
        type_check_expression_statement(statement, manager)
    if type(statement) == block_statement:
        type_check_block_statement(statement, manager)

def type_check_if_statement(statement, manager):
    type_check_expression(statement.if_cond, manager)
    type_check_statement(statement.then_part, manager)
    type_check_statement(statement.else_part, manager)

    if (statement.if_cond.data_type == "boolean" and
        statement.then_part.isTypeCorrect == True and
        statement.else_part.isTypeCorrect == False):
        statement.isTypeCorrect = True

def type_check_while_statement(statement, manager):
    type_check_expression(statement.loop_cond, manager)
    type_check_statement(statement.loop_body, manager)
    
    if (statement.loop_cond.data_type == "boolean" and
        statement.loop_body.isTypeCorrect == True):
        statement.isTypeCorrect = True

def type_check_for_statement(statement, manager):
    type_check_statement(statement.initializer, manager)
    type_check_expression(statement.loop_cond, manager)
    type_check_statement(statement.update_expr, manager)
    type_check_statement(statement.loop_body, manager)
    
    if (statement.initializer.isTypeCorrect == True and
        statement.loop_cond.data_type == "boolean" and
        statement.update_expr.isTypeCorrect == True and
        statement.loop_body.isTypeCorrect == True):
        statement.isTypeCorrect = True

def type_check_return_statement(statement, manager):
    type_check_expression(statement.return_value, manager)
    
    method_return_type = manager.curr_class_body_decl.return_type.type
    
    if statement.return_value == None:
        if method_return_type == "void":
            statement.isTypeCorrect = True

    else:        
        if isSubtype(statement.return_value.data_type, method_return_type, manager.class_table):
            statement.isTypeCorrect = True
    
def type_check_expression_statement(statement, manager):
    type_check_expression(statement.expression, manager)

    if statement.expression.data_type != "error":
        statement.isTypeCorrect = True

def type_check_block_statement(statement, manager):
    for stmt in statement.statements:
        type_check_statement(stmt, manager)

        # This statement is type correct if all the statements in the sequence are type correct.
        if stmt.isTypeCorrect == "error":
            statement.data_type = "error"
            return
    
    statement.isTypeCorrect = True

# statement
# =========================================

# =========================================
# expression

def type_check_expression(expression, manager):
    if expression == None:
        return

    if type(expression) == constant_expression:
        assign_type_constant_expression(expression)
    elif type(expression) == var_expression:
        assign_type_var_expression(expression, manager)
    elif type(expression) == unary_expression:
        assign_type_unary_expression(expression, manager)
    elif type(expression) == binary_expression:
        assign_type_binary_expression(expression, manager)
    elif type(expression) == assign_expression:
        assign_type_assign_expression(expression, manager)
    elif type(expression) == auto_expression:
        assign_type_auto_expression(expression, manager)
    elif type(expression) == field_access_expression:
        assign_type_field_access_expression(expression, manager)
    elif type(expression) == method_call_expression:
        assign_type_method_call_expression(expression, manager)
    elif type(expression) == new_object_expression:
        assign_type_new_object_expression(expression)
    elif type(expression) == this_expression:
        assign_type_this_expression(expression, manager)
    elif type(expression) == super_expression:
        assign_type_super_expression(expression, manager)
    elif type(expression) == class_reference_expression:
        assign_type_class_reference_expression(expression, manager)

def assign_type_constant_expression(expression):
    if type(expression.value) == int:
        expression.data_type = "int"
    elif type(expression.value) == float:
        expression.data_type = "float"
    elif expression.value == "true" or expression.value == "false":
        expression.data_type = "boolean"
    elif expression.value == "null":
        expression.data_type = "null"
    elif type(expression.value) == str:
        expression.data_type = "string"

def assign_type_var_expression(expression, manager):
    variable = None
    
    if type(manager.curr_class_body_decl) is constructor_record:
        for var in manager.curr_class_body_decl.variable_table:
            if var.variable_id == expression.id:
                variable = var
                break
    else:
        for var in manager.curr_class_body_decl.variable_table:
            if var.variable_id == expression.id:
                variable = var
                break

    expression.data_type = variable.type.type

def assign_type_unary_expression(expression, manager):
    type_check_expression(expression.operand, manager)
    
    if expression.operator == "uminus":
        if expression.operand.data_type == "int" or expression.operand.data_type == "float":
            expression.data_type = expression.operand.data_type
        else:
            expression.data_type = "error"
    else:
        if expression.operand.data_type == "boolean":
            expression.data_type = expression.operand.data_type
        else:
            expression.data_type = "error"

def assign_type_binary_expression(expression, manager):
    type_check_expression(expression.fst_operand, manager)
    type_check_expression(expression.snd_operand, manager)

    operator = expression.operator
    fst_data_type = expression.fst_operand.data_type
    snd_data_type = expression.snd_operand.data_type
    
    # Arithmetic Operators
    if (operator == "add" or operator == "sub" or operator == "mul" or
        operator == "div" or operator == "int"):
        if fst_data_type == "int" and snd_data_type == "int":
            expression.data_type = "int"
        elif (fst_data_type == "float" and snd_data_type == "int" or
            fst_data_type == "int" and snd_data_type == "float"):
            expression.data_type = "float"
        else:
            expression.data_type = "error"
    
    # Boolean Operators
    elif operator == "and" or operator == "or":
        if fst_data_type == "boolean" and snd_data_type == "boolean":
            expression.data_type = "boolean"
        else:
            expression.data_type = "error"

    # Arithmetic Comparisons
    elif operator == "lt" or operator == "leq" or operator == "gt" or operator == "geq":
        if (fst_data_type == "float" and snd_data_type == "int" or
            fst_data_type == "int" and snd_data_type == "float"):
            expression.data_type = "boolean"
        else:
            expression.data_type = "error"
        
    # Equality Comparisons
    elif operator == "eq" or operator == "neq":
        # type boolean if type of one operand is subtype of other, else error
        if (isSubtype(fst_data_type, snd_data_type, manager.class_table) or 
            isSubtype(snd_data_type, fst_data_type, manager.class_table)):
            expression.data_type = "boolean"
        else:
            expression.data_type = "error"

def assign_type_assign_expression(expression, manager):
    type_check_expression(expression.lhs, manager)
    type_check_expression(expression.rhs, manager)

    print_expression(expression.lhs)
    print(expression.lhs.data_type)
    print()
    print_expression(expression.rhs)
    print(expression.rhs.data_type)
    if (expression.lhs.data_type != "error" and expression.rhs.data_type != "error" and
        isSubtype(expression.rhs.data_type, expression.lhs.data_type, manager.class_table)):
        expression.data_type = expression.rhs.data_type
    else:
        expression.data_type = "error"

def assign_type_auto_expression(expression, manager):
    type_check_expression(expression.operand, manager)

    if expression.operand.data_type == "int" or expression.operand.data_type == "float":
        expression.data_type = expression.operand.data_type
    else:
        expression.data_type = "error"

def assign_type_field_access_expression(expression, manager):
    
    type_check_expression(expression.base, manager)

    extractedType = "" # holds the type of the expression's base
    isStatic = False # tells whether this is a static field being referred to

    if extractedType.startswith("user"):
        extractedType = extractUserType(expression.base.data_type)

    else:
        extractedType = extractClassLiteralType(expression.base.data_type)
        isStatic = True

    while (curr_class := findClassRecord(extractedType, manager.class_table)) != None:
        for field in curr_class.fields:
            
            # Must have a matching field name
            if field.field_name == expression.field_name:

                if ((isStatic is False and field.field_applicability is "instance") 
                    or (isStatic is True and field.field_applicability is "static" and curr_class.class_name == extractedType)):

                    if field.field_visibility == "public":
                        expression.accessed_id = field.field_id
                        expression.data_type = field.type.type
                        return
                    
                    else:
                        # private
                        if curr_class.class_name == manager.class_table[manager.curr_class_index].class_name:
                            expression.accessed_id = field.field_id
                            expression.data_type = field.type.type
                            return

        curr_class = curr_class.super_name

    expression.data_type = "error"
    
    
def assign_type_method_call_expression(expression, manager):
    type_check_expression(expression.base, manager)

    for param in expression.arguments:
        type_check_expression(param, manager)

    extractedType = "" # holds the type of the expression's base
    isStatic = False # tells whether this is a static field being referred to

    if extractedType.startswith("user"):
        extractedType = extractUserType(expression.base.data_type)

    else:
        extractedType = extractClassLiteralType(expression.base.data_type)
        isStatic = True

    while (curr_class := findClassRecord(extractedType, manager.class_table)) != None:
        for method in curr_class.methods:

            # Must have a matching name
            if method.method_name is expression.method_name:

                # Must have matching applicability
                if ((isStatic is False and method.method_applicability is "instance") 
                    or (isStatic is True and method.method_applicability is "static" and curr_class.class_name == extractedType)):

                    






def assign_type_new_object_expression(expression):
    expression.data_type = "int"

def assign_type_this_expression(expression, manager):
    expression.data_type = "user(" + manager.class_table[manager.curr_class_index].class_name + ")"

def assign_type_super_expression(expression, manager):
    curr_class = manager.class_table[manager.curr_class_index]

    if curr_class.super_name == None:
        expression.data_type = "error"
    else:
        expression.data_type = "user(" + curr_class.super_name + ")"

def assign_type_class_reference_expression(expression, manager):
    if findClassRecord(expression.referred_class_name, manager.class_table) == None:
        expression.data_type = "class-literal(" + expression.referred_class_name + ")"

# expression
# =========================================

# =========================================
# helper functions

# Checks if type1 is a subtype of type2 given a class table. Returns true if it is, false otherwise.
# type1 and type2 are both strings denoting types.
def isSubtype(type1, type2, class_table):

    # Type T is a subtype of itself (i.e., the subtype relation is reflexive).
    if type1 == type2:
        return True
    
    # int is a subtype of float
    elif type1 == "int" and type2 == "float":
        return True
    
    elif "user" in type2:

        # null (type1) is a subtype of user(A) (type2) for any class A
        if type1 == "null":
            return True

        # Extracts the types out of the user-defined type string
        class_type1 = type1[5:(len(type1)-1)]
        class_type2 = type2[5:(len(type2)-1)]
        
        # user(A) is a subtype of user(B) if A is a subclass of B.
        if isSubclass(class_type1, class_type2, class_table):
            return True
        
    else:
        # class-literal(A) is a subtype of class-literal(B) if A is a subclass of B.
        # NOTE: This assumes that type1 and type2 are class names given from the field
        # referred_class_name in class_reference_expressions.
        if isSubclass(type1, type2, class_table):
            return True
    
    return False
        

# Checks if c1 is a subclass of c2. Returns true if it is, false otherwise.
# c1 and c2 are both strings denoting classes.
def isSubclass(c1, c2, class_table):
    
    # Type T is a subtype of itself (i.e., the subtype relation is reflexive).
    if c1 == c2:
        return True
    
    else:
        c1_class_record = findClassRecord(c1, class_table) # the current super class being searched for

        if c1_class_record == None:
           raise Exception("Given class " + c1 + " could not be found!")
        
        curr_super_class_name = c1_class_record.super_name

        # Traverse up the class hierarchy until either the super class is found, or 
        # the super class could not be found.
        while curr_super_class_name != None:

            curr_class_record = findClassRecord(curr_super_class_name, class_table)

            if curr_class_record.class_name == c2:
                return True
            else:
                curr_super_class_name = curr_class_record.super_name
        
        return False


# Given a class name, returns the corresponding class record in the class table.
# Returns the corresponding class record if found in the given class table. None otherwise
def findClassRecord(given_class, class_table):

    for curr_class in class_table:

        if curr_class.class_name == given_class:

            return curr_class
        
    return None



def extractUserType(data_type):
    if data_type.startswith("user"):
        # Extracts the types out of the user-defined type string
        return data_type[5:(len(data_type)-1)]
    
    else:
        raise Exception("Given data type is not user-defined")
    
def extractClassLiteralType(data_type):
        
    if data_type.startswith("class-literal"):
        return data_type[14:(len(data_type)-1)]
    
    else:
        raise Exception("Given data type is not class-literal!")

# helper functions
# =========================================