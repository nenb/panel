import param
import pytest

import panel as pn

from panel.interact import interactive
from panel.layout import Row
from panel.links import CallbackGenerator
from panel.pane import (
    Bokeh, HoloViews, Interactive, IPyWidget, PaneBase, Vega,
)
from panel.param import ParamMethod
from panel.tests.util import check_layoutable_properties

SKIP_PANES = (Bokeh, HoloViews, ParamMethod, interactive, IPyWidget, Interactive, Vega)

all_panes = [w for w in param.concrete_descendents(PaneBase).values()
             if not w.__name__.startswith('_') and not
             issubclass(w, SKIP_PANES)
             and w.__module__.startswith('panel')]


def test_pane_repr(document, comm):
    pane = pn.panel('Some text', width=400)
    assert repr(pane) == 'Markdown(str, width=400)'


@pytest.mark.parametrize('pane', all_panes)
def test_pane_layout_properties(pane, document, comm):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    model = p.get_root(document, comm)
    check_layoutable_properties(p, model)


@pytest.mark.parametrize('pane', all_panes+[Bokeh])
def test_pane_linkable_params(pane, document, comm):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    controls = p.controls(jslink=True)
    layout = Row(p, controls)

    try:
        CallbackGenerator.error = True
        layout.get_root(document, comm)
    except Exception as e:
        raise e
    finally:
        CallbackGenerator.error = False


@pytest.mark.parametrize('pane', all_panes)
def test_pane_clone(pane):
    try:
        p = pane()
    except ImportError:
        pytest.skip("Dependent library could not be imported.")
    clone = p.clone()

    assert ([(k, v) for k, v in sorted(p.param.values().items()) if k not in ('name', '_pane')] ==
            [(k, v) for k, v in sorted(clone.param.values().items()) if k not in ('name', '_pane')])


@pytest.mark.parametrize('pane', all_panes)
def test_pane_signature(pane):
    from inspect import Parameter, signature
    parameters = signature(pane).parameters
    assert len(parameters) == 2
    assert 'object' in parameters
    assert parameters['object'] == Parameter('object', Parameter.POSITIONAL_OR_KEYWORD, default=None)
