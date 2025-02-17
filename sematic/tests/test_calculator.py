# Standard Library
from typing import Any, List, Tuple, Union

# Third-party
import pytest

# Sematic
from sematic.abstract_calculator import CalculatorError
from sematic.calculator import (
    Calculator,
    _convert_lists,
    _convert_tuples,
    _make_list,
    _make_tuple,
    func,
)
from sematic.db.tests.fixtures import test_db  # noqa: F401
from sematic.future import Future
from sematic.resolvers.resource_requirements import (  # noqa: F401
    KubernetesResourceRequirements,
    ResourceRequirements,
)
from sematic.utils.exceptions import ResolutionError


def test_decorator_no_params():
    @func
    def f():
        pass

    assert isinstance(f, Calculator)


def test_decorator_with_params():
    @func()
    def f():
        pass

    assert isinstance(f, Calculator)


def test_any():
    expected = (
        r"Invalid type annotation for argument 'x' "
        r"of sematic.tests.test_calculator.f1: 'Any' is "
        r"not a Sematic-supported type. Use 'object' instead."
    )
    with pytest.raises(TypeError, match=expected):

        @func
        def f1(x: Any) -> None:
            pass

    @func
    def f2(x: object) -> None:
        pass


def test_doc():
    @func
    def f():
        """Some documentation"""
        pass

    assert f.__doc__ == "Some documentation"


def test_name():
    @func
    def abc():
        pass

    assert abc.__name__ == "abc"


def test_not_a_function():
    with pytest.raises(
        TypeError, match=r".*can only be used with functions. But 'abc' is a 'str'."
    ):
        Calculator("abc", {}, None)

    with pytest.raises(
        TypeError, match=r".*can only be used with functions, not methods.*"
    ):

        class SomeClass:
            @func
            def some_method(self: object) -> None:
                pass

    with pytest.raises(
        TypeError,
        match=r".*can't be used with async functions, generators, or coroutines.*",
    ):

        @func
        def a_generator() -> object:
            yield 42

    with pytest.raises(
        TypeError,
        match=r".*can't be used with async functions, generators, or coroutines.*",
    ):

        @func
        async def an_async_func() -> int:
            return 42


def test_inline_and_resource_reqs():
    with pytest.raises(
        ValueError, match="Inline functions cannot have resource requirements"
    ):

        @func(
            inline=True,
            resource_requirements=ResourceRequirements(
                KubernetesResourceRequirements()
            ),
        )
        def abc():
            pass


def test_types_not_specified():
    @func
    def f():
        pass

    assert f.input_types == dict()
    assert f.output_type is type(None)  # noqa: E721


def test_none_types():
    @func
    def f(a: None) -> None:
        pass

    assert f.output_type is type(None)  # noqa: E721
    assert f.input_types == dict(a=type(None))


def test_types_specified():
    @func
    def f(a: float) -> int:
        return int(a)

    assert f.input_types == dict(a=float)
    assert f.output_type is int


def test_variadic():
    with pytest.raises(
        ValueError,
        match=("Variadic arguments are not supported."),
    ):

        @func
        def f(*abc):
            pass


def test_missing_types():
    with pytest.raises(
        ValueError,
        match=(
            "Missing calculator type annotations."
            " The following arguments are not annotated: 'a', 'b'"
        ),
    ):

        @func
        def f(a, b, c: float):
            pass


def test_call_fail_cast():
    @func
    def f(a: float) -> float:
        return a

    with pytest.raises(TypeError, match="Cannot cast 'abc' to <class 'float'>"):
        f("abc")


def test_call_pass_cast():
    @func
    def f(a: float) -> float:
        return a

    ff = f(1.23)

    assert isinstance(ff, Future)
    assert ff.calculator is f
    assert set(ff.kwargs) == {"a"}
    assert isinstance(ff.kwargs["a"], float)
    assert ff.kwargs["a"] == 1.23


def test_call_fail_binding():
    @func
    def f(a: float) -> float:
        return a

    with pytest.raises(TypeError, match="too many positional arguments"):
        f(1, 2)


@func
def foo() -> str:
    return "foo"


@func
def bar() -> str:
    return "bar"


@func
def baz() -> int:
    return 42


def test_make_list():
    future = _make_list(List[str], [foo(), bar()])

    assert isinstance(future, Future)
    assert future.calculator.output_type is List[str]
    assert len(future.calculator.input_types) == 2


def test_make_tuple():
    future = _make_tuple(Tuple[str, int], (bar(), baz()))

    assert isinstance(future, Future)
    assert future.calculator.output_type is Tuple[str, int]
    assert len(future.calculator.input_types) == 2
    assert future.calculator.calculate(v0="a", v1=42) == ("a", 42)


@func
def pipeline() -> List[str]:
    return [foo(), bar(), "baz"]


@func
def tuple_pipeline() -> Tuple[str, int, str]:
    return (foo(), baz(), "qux")


def test_pipeline():
    output = pipeline().resolve(tracking=False)
    assert output == ["foo", "bar", "baz"]


def test_tuple_pipeline():
    output = tuple_pipeline().resolve(tracking=False)
    assert output == ("foo", 42, "qux")


def test_convert_lists():
    result = _convert_lists([1, foo(), [2, bar()], 3, [4, [5, foo()]]])

    assert isinstance(result, Future)
    assert result.props.inline is True
    assert len(result.kwargs) == 5
    assert (
        result.calculator.output_type
        is List[
            Union[
                int, str, List[Union[int, str]], List[Union[int, List[Union[int, str]]]]
            ]
        ]
    )

    assert isinstance(result.kwargs["v1"], Future)
    assert isinstance(result.kwargs["v2"], Future)
    assert isinstance(result.kwargs["v2"].kwargs["v1"], Future)
    assert isinstance(result.kwargs["v4"].kwargs["v1"].kwargs["v1"], Future)

    @func
    def pipeline() -> List[
        Union[
            int,
            str,
            List[Union[int, str]],
            List[Union[int, List[Union[int, str]]]],
        ]
    ]:
        return [1, foo(), [2, bar()], 3, [4, [5, foo()]]]  # type: ignore

    assert pipeline().resolve(tracking=False) == [
        1,
        "foo",
        [2, "bar"],
        3,
        [4, [5, "foo"]],
    ]


def test_convert_tuples():
    value = (42, [1, baz(), 3], (foo(), bar()), foo())
    expected_type = Tuple[int, List[int], Tuple[str, str], str]
    result = _convert_tuples(value, expected_type)
    assert isinstance(result, Future)
    assert result.props.inline is True

    @func
    def pipeline() -> expected_type:
        return value

    assert pipeline().resolve(tracking=False) == (42, [1, 42, 3], ("foo", "bar"), "foo")


def test_inline_default():
    @func
    def f():
        pass

    assert f._inline is True
    assert f().props.inline is True


def test_inline():
    @func(inline=False)
    def f():
        pass

    assert f._inline is False
    assert f().props.inline is False


def test_resource_requirements():
    resource_requirements = ResourceRequirements(
        kubernetes=KubernetesResourceRequirements(node_selector={"a": "b"}, requests={})
    )

    @func(resource_requirements=resource_requirements, inline=False)
    def f():
        pass

    assert f._resource_requirements == resource_requirements
    assert f().props.resource_requirements == resource_requirements


def test_resolve_error():
    @func()
    def f():
        raise ValueError("Intentional error")

    with pytest.raises(ResolutionError) as exc_info:
        # resolving should surface the ResolutionError,
        # with root cause as __context__
        # see https://peps.python.org/pep-0409/#language-details
        f().resolve(tracking=False)

    assert isinstance(exc_info.value.__context__, CalculatorError)
    assert isinstance(exc_info.value.__context__.__context__, ValueError)
    assert "Intentional error" in str(exc_info.value.__context__.__context__)


def test_calculate_error():
    @func()
    def f():
        raise ValueError("Intentional error")

    with pytest.raises(CalculatorError) as exc_info:
        # calling calculate should surface the CalculatorError,
        # with root cause as __context__
        # see https://peps.python.org/pep-0409/#language-details
        f.calculate()

    assert isinstance(exc_info.value.__context__, ValueError)
    assert "Intentional error" in str(exc_info.value.__context__)


@func
def pass_through(x: int) -> int:
    return x


@func
def unused_results_pipeline() -> int:
    x = pass_through(42)
    y = pass_through(x)
    pass_through(y)
    return y


@func
def unused_results_list_pipeline(create_unused: bool) -> List[int]:
    x = pass_through(42)
    y = pass_through(43)
    z = pass_through(44)
    if create_unused:
        return [x, y]
    else:
        return [x, y, z]


def test_unused_future():
    with pytest.raises(ResolutionError, match=r".*output.*does not depend on.*"):
        unused_results_pipeline().resolve(tracking=False)
    with pytest.raises(ResolutionError, match=r".*output.*does not depend on.*"):
        unused_results_list_pipeline(True).resolve(tracking=False)
    unused_results_list_pipeline(False).resolve(tracking=False)
