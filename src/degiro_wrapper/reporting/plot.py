import matplotlib.pyplot as plt
import matplotlib.dates as mdates

FIGKWARGS = dict(bbox_inches="tight", transparent=True)


def plot_report(path, tna, cfs, return_total):

    plot_tna_cfs(path=path, tna=tna, cfs=cfs)
    plot_return_total(path, return_total)


def plot_return_total(path, return_total):

    start = return_total.index[0].strftime("%Y-%m-%d")
    end = return_total.index[-1].strftime("%Y-%m-%d")

    return_total = return_total.mul(100)
    return_total.plot(grid=True)
    plt.xlabel("Date")
    plt.ylabel("Total Return (%)")

    file = path / f"total-return_{start}_{end}.png"
    plt.savefig(file, **FIGKWARGS)


def plot_tna_cfs(path, tna, cfs):

    start = tna.index[0].strftime("%Y-%m-%d")
    end = tna.index[-1].strftime("%Y-%m-%d")

    fig, (top, bottom) = plt.subplots(nrows=2, sharex=True)

    top.plot(tna)
    top.grid(True)
    top.set_ylabel("Total Net Assets (EUR)")

    cfs = cfs.reindex(tna.index, fill_value=0.0)
    cfs = cfs.cumsum()

    bottom.plot(cfs)
    bottom.set_ylabel("Cashflows (EUR)")
    bottom.set_xlabel("Date")
    bottom.grid(True)

    bottom.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1, 3, 6, 9)))
    bottom.xaxis.set_minor_locator(mdates.MonthLocator())
    bottom.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(bottom.xaxis.get_major_locator())
    )

    plt.tight_layout()

    file = path / f"tna-cfs_{start}_{end}.png"
    plt.savefig(file, **FIGKWARGS)

    plt.close()
