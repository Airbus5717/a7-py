"""
Generic type system for A7.

Handles generic type parameters, constraints, and monomorphization.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from src.types import (
    Type, TypeKind, GenericParamType, GenericInstanceType, TypeSet,
    StructType, FunctionType, get_predefined_type_set
)
from src.ast_nodes import ASTNode


@dataclass
class GenericConstraint:
    """
    Represents a constraint on a generic type parameter.

    Examples:
    - $T: Numeric
    - $T: @type_set(i32, i64, f32)
    """
    param_name: str
    type_set: TypeSet

    def check_satisfies(self, concrete_type: Type) -> bool:
        """Check if a concrete type satisfies this constraint."""
        return self.type_set.contains(concrete_type)


@dataclass
class GenericContext:
    """
    Context for generic type instantiation.

    Tracks generic parameters and their concrete type mappings.
    """
    # Parameter name -> GenericParamType
    parameters: Dict[str, GenericParamType]

    # Parameter name -> Constraint
    constraints: Dict[str, GenericConstraint]

    # Parameter name -> Concrete type (during instantiation)
    bindings: Dict[str, Type]

    def __init__(self):
        self.parameters = {}
        self.constraints = {}
        self.bindings = {}

    def add_parameter(self, name: str, constraint: Optional[TypeSet] = None) -> GenericParamType:
        """
        Add a generic type parameter.

        Args:
            name: Parameter name (without $)
            constraint: Optional type constraint

        Returns:
            The created GenericParamType
        """
        param_type = GenericParamType(name=name, constraint=constraint)
        self.parameters[name] = param_type

        if constraint:
            self.constraints[name] = GenericConstraint(name, constraint)

        return param_type

    def bind(self, param_name: str, concrete_type: Type) -> bool:
        """
        Bind a generic parameter to a concrete type.

        Args:
            param_name: Parameter name
            concrete_type: Concrete type to bind

        Returns:
            True if binding succeeded and satisfies constraints
        """
        # Check if parameter exists
        if param_name not in self.parameters:
            return False

        # Check constraint if present
        if param_name in self.constraints:
            constraint = self.constraints[param_name]
            if not constraint.check_satisfies(concrete_type):
                return False

        # Bind the type
        self.bindings[param_name] = concrete_type
        return True

    def get_binding(self, param_name: str) -> Optional[Type]:
        """Get the concrete type bound to a parameter."""
        return self.bindings.get(param_name)

    def is_bound(self, param_name: str) -> bool:
        """Check if a parameter is bound to a concrete type."""
        return param_name in self.bindings

    def all_bound(self) -> bool:
        """Check if all parameters are bound."""
        return len(self.bindings) == len(self.parameters)

    def get_constraint(self, param_name: str) -> Optional[GenericConstraint]:
        """Get the constraint for a parameter."""
        return self.constraints.get(param_name)

    def clear_bindings(self) -> None:
        """Clear all type bindings."""
        self.bindings.clear()


class GenericMonomorphizer:
    """
    Handles monomorphization of generic functions and structs.

    Monomorphization generates specialized versions of generic code
    for each concrete type instantiation.
    """

    def __init__(self):
        # Cache of monomorphized instances
        # (name, type_args) -> specialized AST or symbol
        self.instances: Dict[tuple, any] = {}

    def instantiate_function(
        self,
        func_node: ASTNode,
        type_args: List[Type],
        context: GenericContext
    ) -> Optional[ASTNode]:
        """
        Create a monomorphized instance of a generic function.

        Args:
            func_node: Generic function AST node
            type_args: Concrete type arguments
            context: Generic context with parameters

        Returns:
            Specialized function node, or None if instantiation fails
        """
        func_name = func_node.name or "<anonymous>"

        # Create cache key
        type_arg_tuple = tuple(type_args)
        cache_key = (func_name, type_arg_tuple)

        # Check cache
        if cache_key in self.instances:
            return self.instances[cache_key]

        # Bind type arguments
        param_names = list(context.parameters.keys())
        if len(type_args) != len(param_names):
            return None

        for param_name, type_arg in zip(param_names, type_args):
            if not context.bind(param_name, type_arg):
                # Constraint violation
                return None

        # In a real implementation, we would:
        # 1. Clone the function AST
        # 2. Substitute all generic type references with concrete types
        # 3. Re-run type checking on the specialized version
        # 4. Cache the result

        # For now, we just cache the intent
        specialized_node = func_node  # Placeholder
        self.instances[cache_key] = specialized_node

        return specialized_node

    def instantiate_struct(
        self,
        struct_type: StructType,
        type_args: List[Type]
    ) -> Optional[StructType]:
        """
        Create a monomorphized instance of a generic struct.

        Args:
            struct_type: Generic struct type
            type_args: Concrete type arguments

        Returns:
            Specialized struct type, or None if instantiation fails
        """
        struct_name = struct_type.name or "<anonymous>"

        # Create cache key
        type_arg_tuple = tuple(type_args)
        cache_key = (struct_name, type_arg_tuple)

        # Check cache
        if cache_key in self.instances:
            return self.instances[cache_key]

        # Check parameter count
        if len(type_args) != len(struct_type.generic_params):
            return None

        # In a real implementation, we would:
        # 1. Create a new StructType
        # 2. Substitute generic type parameters in field types
        # 3. Cache the specialized version

        # For now, return the original (placeholder)
        specialized_type = struct_type
        self.instances[cache_key] = specialized_type

        return specialized_type

    def get_instance(self, name: str, type_args: tuple) -> Optional[any]:
        """Get a cached monomorphized instance."""
        cache_key = (name, type_args)
        return self.instances.get(cache_key)

    def has_instance(self, name: str, type_args: tuple) -> bool:
        """Check if an instance exists in the cache."""
        cache_key = (name, type_args)
        return cache_key in self.instances


def resolve_generic_constraint(constraint_node: Optional[ASTNode]) -> Optional[TypeSet]:
    """
    Resolve a generic constraint node to a TypeSet.

    Args:
        constraint_node: Constraint AST node (TYPE_SET or TYPE_IDENTIFIER)

    Returns:
        Resolved TypeSet, or None if no constraint
    """
    if constraint_node is None:
        return None

    # Check for predefined type set by name
    if hasattr(constraint_node, 'type_name'):
        type_set_name = constraint_node.type_name
        predefined = get_predefined_type_set(type_set_name)
        if predefined:
            return predefined

    # Check for inline type set
    if hasattr(constraint_node, 'types'):
        # Would need to resolve each type in the set
        # For now, return None (placeholder)
        pass

    return None


def check_constraint_satisfaction(type_: Type, constraint: GenericConstraint) -> bool:
    """
    Check if a type satisfies a generic constraint.

    Args:
        type_: Type to check
        constraint: Constraint to satisfy

    Returns:
        True if type satisfies constraint
    """
    return constraint.check_satisfies(type_)


def infer_type_arguments(
    generic_params: List[str],
    param_types: List[Type],
    arg_types: List[Type]
) -> Optional[Dict[str, Type]]:
    """
    Infer generic type arguments from function call.

    Args:
        generic_params: Generic parameter names
        param_types: Function parameter types (may contain generic types)
        arg_types: Actual argument types

    Returns:
        Mapping of generic param names to inferred types, or None if inference fails
    """
    # Simple unification-based type inference
    bindings: Dict[str, Type] = {}

    for param_type, arg_type in zip(param_types, arg_types):
        if not unify_types(param_type, arg_type, bindings):
            return None

    # Check that all generic parameters were inferred
    for param_name in generic_params:
        if param_name not in bindings:
            return None

    return bindings


def unify_types(pattern: Type, concrete: Type, bindings: Dict[str, Type]) -> bool:
    """
    Unify a type pattern (possibly containing generics) with a concrete type.

    Args:
        pattern: Type pattern (may contain GenericParamType)
        concrete: Concrete type
        bindings: Current type bindings (modified in-place)

    Returns:
        True if unification succeeded
    """
    # If pattern is a generic parameter
    if isinstance(pattern, GenericParamType):
        param_name = pattern.name

        # Check if already bound
        if param_name in bindings:
            # Must match existing binding
            return bindings[param_name].equals(concrete)
        else:
            # Check constraint if present
            if pattern.constraint and not pattern.constraint.contains(concrete):
                return False

            # Bind the type
            bindings[param_name] = concrete
            return True

    # If pattern is a generic instance, unify recursively
    if isinstance(pattern, GenericInstanceType) and isinstance(concrete, GenericInstanceType):
        if pattern.base_name != concrete.base_name:
            return False

        if len(pattern.type_args) != len(concrete.type_args):
            return False

        for p_arg, c_arg in zip(pattern.type_args, concrete.type_args):
            if not unify_types(p_arg, c_arg, bindings):
                return False

        return True

    # Otherwise, types must be equal
    return pattern.equals(concrete)
