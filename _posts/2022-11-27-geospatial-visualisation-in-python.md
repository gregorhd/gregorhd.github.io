---
layout: post
title: One library to rule them all? Geospatial visualisation tools in Python
subtitle: The state of play in mid-2021
description: >-
  A comparison of static and interactive geospatial visualisation libraries in Python.
image: >-
  /assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/python_visualisation_landscape_dark.jpg
optimized_image: >-
  /assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/python_visualisation_landscape_dark.jpg
category: research
tags:
  - Python
  - geospatial
  - visualisation
  - cartopy
  - GeoPandas
  - Altair
  - geoplot
  - datashader
  - GeoViews
  - hvPlot
  - Bokeh
  - Plotly
author: gregorherda
paginate: true
---

_Let's assume you wanted to get a first handle on the impressive array of geospatial visualisation capabilities for dealing with vector data in the Python ecosystem. Where would you even **start**_?

| [**TL;DR: Jump to Graphical Abstract**](#tldr-graphical-abstract) |


- [Library selection](#library-selection)
- [Library comparison](#library-comparison)
- [Results](#results)
  - [Documentation](#documentation)
  - [Code complexity](#code-complexity)
  - [CPU runtime](#cpu-runtime)
    - [Static visualisations](#static-visualisations)
    - [Interactive visualisations](#interactive-visualisations)
- [TL;DR: Graphical Abstract](#tldr-graphical-abstract)
- [Caveats](#caveats)


The good news is, there are plenty of Python libraries to choose from. And the bad news? There are _plenty_ of Python libraries to choose from…

Just to give you a taste, Jake Vander Plas' [excellent talk](https://www.youtube.com/watch?v=FytuB8nFHPQ) on and—meta alert!—visualisation of the Python visualisation landscape served as the basis for this (surely incomplete) [mind map](https://www.mindomo.com/mindmap/the-python-visualisation-landscape-dark-fd1a5c3770bdf84be045094f15ed3b7a). Some libraries with geospatial functionalities are highlighted.

[![Python visualisation landscape](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/python_visualisation_landscape_dark.jpg)](https://www.mindomo.com/mindmap/the-python-visualisation-landscape-dark-fd1a5c3770bdf84be045094f15ed3b7a)

So again, where to start?

My supervisor at Ulster University (UU) [Robert McNabb](https://pure.ulster.ac.uk/en/persons/robert-mcnabb) and I tried to answer this question in mid-2021 in what then became my MSc thesis and a significantly amended paper available as [a preprint](https://cs.paperswithcode.com/paper/python-for-smarter-cities-comparison-of). The codebase can be found [on Github](https://github.com/gregorhd/mapcompare). As such, this post comes a bit late but I hope some of it may still be relevant in late 2022.

| **_Disclaimer_**: This work was my very first foray into Python about 18 months ago. I've since come to more fully appreciate the complexity of real-world use cases and production environments which go way beyond trying to visualise vector data on a local machine (the fictional "scenario" I conjured up at the time), but as a first set of data points, I still think such a comparison can be useful. |

## Library selection

First, I tried to get a very broad overview of what's out there. I looked at various metadata for different libraries supporting geospatial visualisation, eventually creating a **long list** with the help of [pyviz.org](https://pyviz.org/tools.html) and other excellent resources. I compared input and output formats, other libraries central to implementation, ease of installation and some proxy indicators suggesting the vibrancy of the developer and user community.

Next, I winnowed things down to a **short list**.

The short list tried to include both large-community projects (e.g., [_Bokeh_](https://bokeh.org/) and [_Plotly_](https://plotly.com/python/)) as well as those relying on much fewer contributors (e.g., [_geoplot_](https://residentmario.github.io/geoplot/)). Since most help you'll need will end up coming from (largely unpaid) contributors, I figured all short-listed libraries needed to show on-going development in the last year (hence the exclusion, at the time, of [_mplleaflet_](https://github.com/jwass/mplleaflet) and [_geoplotlib_](https://github.com/andrea-cuttone/geoplotlib)). Also, to remove the confounding variable of connection speeds from my simplistic performance metric, I decided they had to be able to plot geometries without employing a Web Tile Service (hence the exclusion of [_folium_](https://python-visualization.github.io/folium/)). Finally, I was looking for a good mix of backends and both imperative as well as declarative approaches (such as [_Altair_](https://altair-viz.github.io/)), resulting in this final short list across both a static and interactive track of comparison.

![Short-list of geospatial visualisation libraries](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/short_list.jpg)

The magical [_datashader_](https://datashader.org/) was included in the static track 'out of competition', to first demonstrate its 'as-is' functionality before employing it in the interactive track with a core plotting library.

## Library comparison

With our contestants selected and waiting in the wings, it was time to prepare the "arena".

The battleground was a simple visualisation task performed—on my laptop—for both a "complete" dataset and a smaller subset. The complete dataset contained 144,727 polygons representing the city of [Dresden's cadastral building footprints](https://www.geodaten.sachsen.de/downloadbereich-alkis-4176.html). The subset contained 2,645 features from the same dataset.

Both datasets were stored in locally hosted PostGIS databases and queried via [GeoPandas'](https://geopandas.org/en/stable/) ``from_postgis()`` function, returning GeoDataFrames to serve as primary data inputs (more on data acquisition and preparation [here](https://github.com/gregorhd/mapcompare/blob/main/data/README.md)).

The short-listed libraries were compared with regards to:

1. the range of available **documentation**, based on common documentation 'elements' and code examples consulted to implement the task;
2. the **number of lines of code** needed to reproduce the common map template, excluding comments and blank lines. While a very much subjective measure, a relatively similar level of intermediate assignment statements across libraries was attempted;
3. the ability to **reproduce the map template** including a legend and base map;
4. "resource requirements" (simply output file size after export to SVG/PNG or HTML; for interactive visualisations, a subjective assessment of 'responsiveness' on pan and zoom);
5. and the **cumulative CPU runtime** required for the main ``renderFigure()`` function to complete, averaged across a total of 10 runs. To increase comparability, the rendering function excluded both data acquisition and any data pre-processing, reprojection or conversion steps. CPU runtimes were measured using the [_cProfile_](https://docs.python.org/3/library/profile.html#module-cProfile) module. For the interactive track, as rendering is ultimately performed by the execution of JavaScript code, _cProfile_ will not capture the entirety of the processing costs (see also the table with some code "adjustments" just above the [Results](https://github.com/gregorhd/mapcompare#results) section on Github as well as the [Caveats](#caveats) section for more on this).

## Results

### Documentation

Good documentation is everything. Sadly, often these pages don't get the love (or funding) they deserve. But things are improving considerably and today I am quite amazed at the pedagogical skill with which new concepts are being introduced to learners, making ample use of the beloved Jupyter Notebook.

It seems that the structure and content of documentation in the Python world has coalesced into a near standard containing a set of reoccurring **elements**.

A **quick start** or **getting started** section can be found on the documentation pages of most libraries. These are almost always structured as explanatory text alternating with code snippets exemplifying a feature or best practice. While straight-forward, new learners without a background in data science or mathematics may find this an initial hurdle, especially once more advanced features are demonstrated. Finding the right range and difficulty of examples for students of different backgrounds is a known problem in data science education in general. Python-based data visualisation is no exception here.

While "getting started" sections are available as static web pages, they are often simply conversions of Jupyter Notebooks which allow users to edit and execute code cells themselves in a locally-run Python kernel and have plots be generated in the browser.

A second element were more extensive **user guides**. These often cover advanced features and concepts of increasing complexity.

Thirdly, all libraries, except [_hvPlot_](https://hvplot.holoviz.org/), featured an **API reference** which can be thought of as the official 'code registry' or 'code index' hierarchically listing all functions and classes accessible to users as well as requirements for positional or keyword arguments. API references largely reproduce the "doc strings", or non-code explanatory text, appended to a function, method, or class definition. Except for more advanced users, the API reference rarely serves as the first learning resource but is essential if you really want to understand error messages or explore more advanced features.

Finally, don't forget the **example galleries** or **reference galleries**. These provide output examples along with the sample data and underlying code, and can significantly flatten your learning curve.

Not in all cases, however, will this 'formally provided' documentation help you understand what's happening. Therefore, you may find yourself going down some rather obscure rabbit holes on GitHub and StackOverflow, which can be a real lottery: Depending on the size of the user base, and assuming your problem matches somebody's prior knowledge, questions are often resolved in a matter of hours. Other times, responses may never materialise or fail to address your issue (maybe because a fix is not due until the next major release). I encountered both scenarios, though the latter much less often.

**The gist on documentation:** For this study, the degree to which I had to ask around varied significantly between libraries, with some requiring multiple elaborate questions to be posted (e.g. [_GeoViews_](https://geoviews.org/)_, datashader_, _Altair_), others (e.g. [_Cartopy_](https://scitools.org.uk/cartopy/docs/latest/)_, GeoPandas, Plotly.py_) requiring no interaction. Where it _was_ necessary, this could be due to a genuine gap in documentation or my own spotty understanding.

### Code complexity

While anything but a scientific measure of comparison, I did find that the level of verbosity differed widely for this very simple plotting task, where more succinct, high-level APIs did not, in my view, sacrifice functionality or customisability.

|**Static**|**Interactive**|
|--|--|
| ![Lines of code comparison for static visualisations in Python](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/code_comparison_static_dark.jpg) | ![Lines of code comparison for interactive visualisations in Python](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/code_comparison_interactive_dark.jpg) |

For static visualisations, you can see that code complexity, by this measure, is largely comparable. Especially with non-geospatial use cases from traditional data science, declarative approaches can be far more economical once key and value dimensions are declared. Due to the imperative nature of the plotting task at hand, this relative advantage of declarative approaches could not really materialise here.

In the interactive track, things got a bit more interesting.

_Plotly.py_'s syntax was the most complex despite employing the more user friendly _Plotly Express_ interface. This is because one, apparently (?), has to write the data to disk into an intermediary [JSON file](https://plotly.com/python/mapbox-county-choropleth/). Therefore, _Plotly.py_'s line count remains high even without adding auto zoom functionality (which may be available out of the box by now).

_GeoViews_ and, especially, _hvPlot_ significantly simplify interacting with _Bokeh_'s standard API, with widely varying costs to overall performance.

### CPU runtime

#### Static visualisations

| **Subset** | **Complete** |
| --- | --- |
| ![CPU runtime comparison for static visualisations in Python - subset](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/runtime_comparison_static_subset_dark.jpg) | ![CPU runtime comparison for static visualisations in Python - complete](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/runtime_comparison_static_complete_dark.jpg) |


Of the three [_Matplotlib_](https://matplotlib.org/)-based libraries, _Cartopy_ marginally outperformed _GeoPandas,_ while _Altair_'s interface to [_Vega-Lite_](https://vega.github.io/vega-lite/) ran three times longer than these two _Matplotlib_ interfaces.

The stark difference of _geoplot_'s performance to, for instance, _Cartopy_ may be due to different entry points to _Matplotlib_, which is a massively complex library at this point and thus proved too tough a nut to crack in the time available.

In case you're interested: _Datashader_'s large standard deviation of 1.853 seconds with a mean of 1.564 seconds is due to its use of the [_Numba_](https://dl.acm.org/doi/abs/10.1145/2833157.2833162) compiler, which provides similar performance to a traditional compiled language. The significant performance gains materialise only after compilation in the first run which you can see very nicely below in the individual _datashader_ CPU runtimes in this 10-run loop.

| **run #** | **time** | **run #** | **time** |
| --- | --- | --- | --- |
| **1** | **6.837** | 6 | 0.993 |
| 2 | 0.946 | 7 | 1.000 |
| 3 | 0.979 | 8 | 0.967 |
| 4 | 1.032 | 9 | 0.961 |
| 5 | 0.972 | 10 | 0.951 |

#### Interactive visualisations

| **Subset** | **Complete** |
| --- | --- |
| ![CPU runtime comparison for interactive visualisations in Python - subset](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/runtime_comparison_interactive_subset_dark.jpg) | ![CPU runtime comparison for interactive visualisations in Python - complete](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/runtime_comparison_interactive_complete_dark.jpg) |

Surprising were the stark differences in runtime between the three _Bokeh_-based implementations making no use of _datashader_: interfacing with _Bokeh_ through _hvPlot_ proved to be 3.7 times faster than interacting with _Bokeh_ through _GeoViews_. Engaging with _Bokeh_'s API directly outperformed _hvPlot_ and _GeoViews_ by a factor of 15.5 and 58, respectively. Despite consultations with the developers, I was not able to pin down the reasons for _GeoView's_ poor performance. One possible explanation could be the additional layers of abstraction between _GeoViews_ and _Bokeh_ (via _HoloViews_), although _hvPlot_ employs an even higher level of abstraction and, also being a HoloViz product, has similar dependencies—but without incurring a similar penalty.

**The interactive "performance winner" is** the combination of _GeoViews + datashader + Bokeh Server_, combining _Bokeh's_ interactive features with low client-side resource use. Below you can see this combination in action. Building footprints are being rasterised by _datashader_ on-the-fly at ever higher resolutions as you zoom in while preserving the ability to interactively access the polygons' attributes via the hover tool.

![GeoViews + datashader + Bokeh Server](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/geoviews_datashader_bokeh_dresden.gif)

## TL;DR: Graphical Abstract

![Geospatial visualisation in Python – Graphical abstract](/assets/img/uploads/2022-11-27-geospatial-visualisation-in-python/graphical_abstract.jpg)

## Caveats

1. All of the short-listed libraries employ multiple complex technologies, some of which outside the Python ecosystem (e.g., the JavaScript libraries underlying both _Bokeh_ and _Plotly.py_). Due to these confounding variables, and even with the various code adjustments mentioned above, I most certainly failed to establish a truly level playing field with regard to comparing CPU runtimes. What the _cProfile_ results show is simply indicative of the user experience and the approximate time required to generate a map product on screen.
2. Lines of code is a poor measure for code complexity. Alternatively, one could see groups of experts for each implementation develop a 'best practice' code sample, though I'm sceptical this would increase comparability (or would be feasible in practice).
3. The static map products would not be considered useful outputs in most real-world scenarios: due to significant overplotting, a building-level analysis would rarely be presented at such a small representative fraction. And as for the interactive products, except for live server-side aggregation and rasterisation as demonstrated by the _GeoViews_ + _datashader_ + _Bokeh Server_ implementation, serving large quantities of geospatial data over the web would nowadays probably involve prior conversion to raster or vector tiles.
4. The simplicity of the visualisation task meant that more advanced, and for users such as local authorities potentially more interesting, use cases such as dashboarding were not demonstrated. If this is something you'd like to explore, do check out _Bokeh_'s and _Plotly_'s native dashboarding capabilities ([Dash](https://dash.plotly.com/)) as well as HoloViz's [Panel](https://panel.holoviz.org/) library including its app gallery on [awesome-panel.org](https://awesome-panel.org/gallery) for inspiration.
5. Due to the interconnectedness of the Python ecosystem, a library's functionalities and performance can never be solely attributed to its own codebase.
6. Finally, all libraries as well as their dependencies are under constant development. As such, the state of play outlined here represents merely a snapshot as of mid-2021.

I hope you enjoyed watching my younger self learn about these exciting new technologies, and maybe some of this was insightful for you as well.

Do leave a comment and let me know what you think 😊