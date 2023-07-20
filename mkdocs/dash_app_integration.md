# Dash apps 🤝

This documentation page describes how you can integrate `plotly-resampler` in a [dash](https://dash.plotly.com/) application.

Examples of dash apps with `plotly-resampler` can be found in the
[examples folder](https://github.com/predict-idlab/plotly-resampler/tree/main/examples) of the GitHub repository.

## Registering callbacks in a new dash app

When you add a `FigureResampler` figure in a basic dash app, you should:

- Add a [trace-updater component](https://github.com/predict-idlab/trace-updater) to the dash app layout.

      - It should have as `gID` the id of the [dcc.Graph](https://dash.plotly.com/dash-core-components/graph)
        component that contains the `FigureResampler` figure.

- Register the [`FigureResampler`][figure_resampler.FigureResampler] figure its callbacks to the dash app.

      - The id of the [dcc.Graph](https://dash.plotly.com/dash-core-components/graph) component that contains the
      [`FigureResampler`][figure_resampler.FigureResampler] figure and the id of the trace-updater component should be passed to the
      [`register_update_graph_callback`][figure_resampler.FigureResampler.register_update_graph_callback] method.

**Code illustration**:

```python
# Construct the to-be resampled figure
fig = FigureResampler(px.line(...))

# Construct app & its layout
app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="graph-id", figure=fig),
        trace_updater.TraceUpdater(id="trace-updater", gdID="graph-id"),
    ]
)

# Register the callback
fig.register_update_graph_callback(app, "graph-id", "trace-updater")
```

!!! warning

    The above example serves as an illustration, but uses a _global variable_ to store the `FigureResampler` instance;
    this is not a good practice. Ideally you should cache the `FigureResampler` per session on the server side.
    In our [examples folder](https://github.com/predict-idlab/plotly-resampler/tree/main/examples),
    we provide several dash app examples where we perform server side caching of such figures.

!!! tip

    You can make the resampling faster by ensuring the [TraceUpdater](https://github.com/predict-idlab/trace-updater)
    its `sequentialUpdate` argument is set to `False`.

## Limitations

`plotly_resampler` relies on [TraceUpdater](https://github.com/predict-idlab/trace-updater)
to ensure that the _updateData_ is sent efficiently to the front-end.

To enable dynamic-graph-construction, plotly-resampler supports [pattern matching callbacks](https://dash.plotly.com/pattern-matching-callbacks).
This could only be achieved by performing partial id matching on the graph-div ID within the `TraceUpdater` component.
This causes the following:

!!! warning "Attention"

    `TraceUpdater` will determine the html-graph-div by performing **partial matching on the “id” property** (using _gdID_)
    of all divs with `#!html classname="dash-graph"`.
    So if multiple same graph-div IDs are used, or one graph-div-ID is a subset of other(s),
    multiple eligible _graph-divs_ will be found and a `SyntaxError` will be raised.

This can be circumvented by using an `uuid`-str for each graph-div, as done in this
[dynamic graph construction example](https://github.com/predict-idlab/plotly-resampler/blob/main/examples/dash_apps/construct_dynamic_figures.py).
