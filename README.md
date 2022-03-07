# jupyterlab-lightweight-charts-jesse
lightweight-charts integration with jupyterlab, using jesse framework to import candles and and use indicators but you can do it with other libraries and sources

This repository comes with idea and initial source of [lightweight-charts-jupyter-bridge](https://github.com/tartakovsky/lightweight-charts-jupyter-bridge) of tartakovsky. Big thanks to him.

For additional information about Jupyter notebooks on Jesse [take a look here](https://docs.jesse.trade/docs/research/jupyter.html)

I added some new features to the original library `lightweight.py`:
- Candlestick chart
- Volume histogram
- Line indicators with same timeframe of candles (optional)
- Line indicators with an higher timeframe (optional)
- Dark Theme parameter (optional)
- Width and Height parameter (optional)

In the jupyterlab file I set:
- wide view of cells (why using them so small?  :) )
- first cell just import, installation and a simple function definition
- the second cell is the main example with a 5' chart with canldes, volume and indicators, two of them are relative to an higher timeframe (1H) 
- In the third cell of the jupyter lab file you can see an example of a simpler chart with just one timeframe (1H) with two indicators data (it's the highter timeframe of the previous example)

![Animated example](jupyterlab_lightweightchart_example.gif)

