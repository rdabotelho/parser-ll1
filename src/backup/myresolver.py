from abc import ABC, abstractmethod
from enum import Enum
from myexceptions import *
from mynode import Node
import re

PATTERN_INTEGER = r'^[+-]?\d+$'
PATTERN_FLOAT = r'^[+-]?\d+(\.\d+)?$'

class ResolverType(Enum):
    PROPERTY = 0,
    METHOD = 1,
    LITERAL = 2,
    OPERATOR = 3

class Resolver(ABC):
    type = None

    @abstractmethod
    def sem(self, node: Node, context: any):
        pass
    
    @abstractmethod
    def eval(self, node: Node, context: any) -> any:
        pass

class PropertyResolver(Resolver):
    type = ResolverType.PROPERTY

    def sem(self, node: Node, object: any):
        if not hasattr(object, node.token.value):
            raise SemanticException(f'Property "{node.token.value}" not found')
        
    def eval(self, node: Node, object: any) -> any:
        result = getattr(object, node.token.value)
        return node.evalChildren(result)

AVAILABLE_METHODS = {
    "replace": 2,
    "upper": 0, 
    "lower": 0, 
    "equals": 1,
    "concate": 1,
    "mask": 1
}

class MethodResolver(Resolver):
    type = ResolverType.METHOD

    def sem(self, node: Node, object: any):
        if not node.token.value in AVAILABLE_METHODS:
            raise SemanticException(f'Method "{node.token.value}" not found')
        args_count = AVAILABLE_METHODS[node.token.value]
        if node.paramCount() != args_count:
            raise SemanticException(f'Method "{node.token.value}" must have {args_count} argument(s)')
        
    def eval(self, node: Node, object: any) -> any:
        result = None
        if node.token.value == 'replace':
            result = object.replace(node.evalParam(0), node.evalParam(1))
        elif node.token.value == 'upper':
            result = object.upper()
        elif node.token.value == 'lower':
            result = object.lower()
        elif node.token.value == 'equals':
            result = object == node.evalParam(0)
        elif node.token.value == 'concate':
            result = f'{object}{node.evalParam(0)}'
        elif node.token.value == 'mask':
            result = self.mask(object, node.evalParam(0))
        return node.evalChildren(result)

    def mask(self, input, pattern):
        result = ''
        input_index = 0
        for char in pattern:
            if char == '#':
                result += input[input_index]
                input_index += 1
            else:
                result += char

        return result

class LiteralResolver(Resolver):
    type = ResolverType.LITERAL

    def sem(self, node: Node, object: any):
        return None
            
    def eval(self, node: Node, object: any) -> any:
        result = node.token.value.replace("'", "")
        if re.fullmatch(PATTERN_INTEGER, result) is not None:
            return int(result)
        elif re.fullmatch(PATTERN_FLOAT, result) is not None:
            return float(result)
        elif result == 'true':
            return True
        elif result == 'false':
            return False
        else:
            return result

class OperatorResolver(Resolver):
    type = ResolverType.OPERATOR

    def sem(self, node: Node, object: any):
        return None
    
    def has_decimal(self, number):
        return number != int(number)            
    
    def eval(self, node: Node, object: any) -> any:
        oper = node.token.value
        left = node.children[0].eval(object)
        if len(node.children) > 1:
            right = node.children[1].eval(object)
        else:
            right = None
        result = 0
        if oper == '+':
            result = left + right
        elif oper == '-':
            result = left - right
        elif oper == '*':
            result = left * right
        elif oper == '/':
            result = left / right
        elif oper == '==':
            return left == right
        elif oper == '!=':
            return left != right
        elif oper == '>':
            return left > right
        elif oper == '<':
            return left < right
        elif oper == '>=':
            return left >= right
        elif oper == '<=':
            return left <= right
        elif oper == 'and':
            return left and right
        elif oper == 'or':
            return left or right
        elif oper == 'not':
            return not left
        if (self.has_decimal(result)):
            return result
        else:
            return int(result)

resolvers = {
    ResolverType.PROPERTY: PropertyResolver(),
    ResolverType.METHOD: MethodResolver(),
    ResolverType.LITERAL: LiteralResolver(),
    ResolverType.OPERATOR: OperatorResolver()
}