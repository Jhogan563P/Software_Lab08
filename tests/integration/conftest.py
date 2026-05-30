try:
    import pydantic.typing as ptyping

    def _evaluate_forwardref_compat(type_, globalns=None, localns=None):
        if hasattr(type_, "_evaluate"):
            try:
                return type_._evaluate(globalns, localns, set())
            except TypeError:
                return type_._evaluate(globalns, localns, recursive_guard=set())
        return type_

    ptyping.evaluate_forwardref = _evaluate_forwardref_compat
except Exception:
    pass
