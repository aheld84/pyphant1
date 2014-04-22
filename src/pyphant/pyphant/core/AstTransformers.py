from pyphant.quantities import Quantity
from ast import (NodeTransformer, fix_missing_locations, Name, Load,
                 BinOp, Num, Mult, Compare, BoolOp, And, Add, Sub, Div, Or,
                 Call, Not, Expression)


class LocationFixingNodeTransformer(NodeTransformer):
    def visit(self, *args, **kargs):
        result = NodeTransformer.visit(self, *args, **kargs)
        fix_missing_locations(result)
        return result


class ReplaceName(LocationFixingNodeTransformer):
    def __init__(self, sampleContainer):
        self.localDict = {}
        self.count = 0
        self.sc = sampleContainer

    def visit_Call(self, node):
        if isinstance(node.func, Name) and node.func.id.lower() == 'col':
            newName = self.getName(self.sc[node.args[0].s])
            return Name(newName, Load())

    def visit_Str(self, node):
        quantity = Quantity(node.s)

        class QuantityDummy(object):
            pass

        dummy = QuantityDummy()
        dummy.unit = Quantity(1.0, quantity.unit)
        dummy.data = quantity.value
        dummy.dimensions = None
        newName = self.getName(dummy)
        return Name(newName, Load())

    def getName(self, ref):
        newName = "N%s" % self.count
        self.count += 1
        self.localDict[newName] = ref
        return newName


def withFactor(factor, node):
    if not isinstance(factor, float):
        raise ValueError('Incompatible units!')
    if factor == 1.0:
        return node
    return BinOp(Num(factor), Mult(), node)


class ReplaceCompare(LocationFixingNodeTransformer):
    def __init__(self, localDict):
        self.localDict = localDict

    def visit_Compare(self, node):
        self.generic_visit(node)
        unitcalc = UnitCalculator(self.localDict)
        leftUD = unitcalc.getUnitAndDim(node.left)
        listUD = [unitcalc.getUnitAndDim(comp) for comp in node.comparators]
        nonNoneDims = [ud[1] for ud in listUD + [leftUD] if ud[1] is not None]
        for dims in nonNoneDims:
            checkDimensions(nonNoneDims[0], dims)
        factorlist = [ud[0] / leftUD[0] for ud in listUD]
        newComplist = [withFactor(*t) \
                       for t in zip(factorlist, node.comparators)]
        compOp = Compare(node.left, node.ops, newComplist)
        compOpTrans = self.compBreaker(compOp)
        return compOpTrans

    def compBreaker(self, node):
        assert isinstance(node, Compare)
        if len(node.comparators) == 1:
            return node
        else:
            comp1 = Compare(node.left, node.ops[0:1],
                            node.comparators[0:1])
            comp2 = Compare(node.comparators[0],
                            node.ops[1:], node.comparators[1:])
            newNode = BoolOp(And(), [comp1, self.compBreaker(comp2)])
            return newNode


class ReplaceOperator(LocationFixingNodeTransformer):
    def __init__(self, localDict):
        self.localDict = localDict

    def visit_BinOp(self, node):
        self.generic_visit(node)
        unitcalc = UnitCalculator(self.localDict)
        leftUD = unitcalc.getUnitAndDim(node.left)
        rightUD = unitcalc.getUnitAndDim(node.right)
        checkDimensions(leftUD[1], rightUD[1])
        if isinstance(node.op, (Add, Sub)):
            factor = rightUD[0] / leftUD[0]
            right = withFactor(factor, node.right)
            binOp = BinOp(node.left, node.op, right)
            return binOp
        elif isinstance(node.op, (Mult, Div)):
            return node
        else:
            raise NotImplementedError('%s not implemented' % (node.op, ))

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, And):
            func = 'logical_and'
        elif isinstance(node.op, Or):
            func = 'logical_or'
        else:
            raise NotImplementedError('%s not implemented' % (node.op, ))
        return self.boolOpBreaker(node.values, func)

    def boolOpBreaker(self, values, func):
        if len(values) == 1:
            return values[0]
        else:
            return Call(Name(func, Load()),
                        [values[0], self.boolOpBreaker(values[1:], func)],
                        [], None, None)

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, Not):
            return Call(Name('logical_not', Load()), [node.operand],
                        [], None, None)
        else:
            raise NotImplementedError('%s not implemented' % (node.op, ))


class UnitCalculator(object):
    def __init__(self, localDict):
        self.localDict = localDict

    def getUnitAndDim(self, node):
        if isinstance(node, Expression):
            return self.getUnitAndDim(node.body)
        elif isinstance(node, Name):
            if node.id in ['True', 'False']:
                return (1.0, None)
            else:
                column = self.localDict[node.id]
                return (column.unit, column.dimensions)
        elif isinstance(node, Num):
            return (1.0, None)
        elif isinstance(node, Call):
            if not isinstance(node.func, Name):
                raise NotImplementedError(
                    'Dynamic functions are not implemented!')
            funcId = node.func.id
            if funcId in ['logical_and', 'logical_or']:
                left = self.getUnitAndDim(node.args[0])
                right = self.getUnitAndDim(node.args[1])
                dimensions = checkDimensions(left[1], right[1])
                if not isinstance(left[0], float):
                    raise ValueError(
                        "Type %s cannot be interpreted as a Boolean" % left)
                if not isinstance(right[0], float):
                    raise ValueError(
                        "Type %s cannot be interpreted as a Boolean" % right)
                return (1.0, dimensions)
            elif funcId == 'logical_not':
                return self.getUnitAndDim(node.args[0])
            else:
                raise NotImplementedError("Function '%s' not implemented" \
                                          % (funcId, ))
        elif isinstance(node, BinOp):
            left = self.getUnitAndDim(node.left)
            right = self.getUnitAndDim(node.right)
            dimensions = checkDimensions(left[1], right[1])
            if isinstance(node.op, (Add, Sub)):
                if not isinstance(left[0] / right[0], float):
                    raise ValueError("units %s, %s not compatible" \
                                     % (left, right))
                unit = left[0]
            elif isinstance(node.op, Mult):
                unit = left[0] * right[0]
            elif isinstance(node.op, Div):
                unit = left[0] / right[0]
            else:
                raise NotImplementedError()
            return (unit, dimensions)
        elif isinstance(node, Compare):
            left = self.getUnitAndDim(node.left)
            nonNoneDims = []
            if left[1] is not None:
                nonNoneDims.append(left[1])
            for comparator in node.comparators:
                right = self.getUnitAndDim(comparator)
                if right[1] is not None:
                    nonNoneDims.append(right[1])
                if not isinstance(left[0] / right[0], float):
                    raise ValueError("units %s, %s not compatible" \
                                     % (left[0], right[0]))
            if len(nonNoneDims) >= 1:
                for dims in nonNoneDims:
                    checkDimensions(nonNoneDims[0], dims)
                dimensions = nonNoneDims[0]
            else:
                dimensions = None
            return (1.0, dimensions)
        else:
            raise NotImplementedError()


def checkDimensions(dimensions1, dimensions2):
    if dimensions1 is not None and dimensions2 is not None and \
           dimensions1 != dimensions2:
        msg = 'Dimensions "%s" and "%s" do not match!' \
              % (dimensions1, dimensions2)
        raise ValueError(msg)
    return dimensions1 or dimensions2
