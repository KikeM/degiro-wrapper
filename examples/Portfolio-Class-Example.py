# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent,md
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import matplotlib.pyplot as plt

from degiro_wrapper.portfolio import Portfolio

# %%
portfolio = Portfolio(path_config="~/degiro-wrapper/degiro.ini")

# %%
portfolio.build_portfolio(start="20190101")

# %%
fig, axes = plt.subplots(nrows =3, figsize = (10, 10), gridspec_kw=dict(hspace = 0.40))


portfolio.returns_ss.mul(100).plot.hist(bins = 50, ax = axes[0])
axes[0].set_title("Daily returns")
axes[0].grid()

portfolio.weights_df.reindex(portfolio.returns_ss.index).plot.area(ax = axes[1])
axes[1].set_title("Exposure")
axes[1].set_xlabel("")
axes[1].legend(ncol = 2, loc = (1.01,0.0))

portfolio.return_total_ss.mul(100).plot(ax = axes[-1]);
axes[-1].set_title("TMWR")
axes[-1].set_ylabel("%")
axes[-1].grid()
