"""Utils."""
import functools
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import patches


class IndexTracker:
    """Provides onscroll and update methods for matplotlib scroll_event."""
    def __init__(self, ax, frames, frame_names, scroll_step=1, **kwargs):
        self.ax = ax
        self.frames = frames
        self.step = scroll_step
        self.frame_names = frame_names
        self.img_kwargs = kwargs
        self.ind = len(frames) // 2
        self.update()

    def onscroll(self, event):
        """Onscroll method."""
        print("%s %s" % (event.button, event.step))
        if event.button == 'up':
            self.ind = np.clip(self.ind + self.step, 0, len(self.frames) - 1)
        else:
            self.ind = np.clip(self.ind - self.step, 0, len(self.frames) - 1)
        self.update()

    def update(self):
        """Update method."""
        self.ax.clear()
        img = self.frames[self.ind]
        self.ax.imshow(img.T, **self.img_kwargs)
        self.ax.set_title('%s' % self.frame_names[self.ind])
        self.ax.set_aspect('auto')
        self.ax.set_ylim([img.shape[1], 0])
        self.ax.set_xlim([0, img.shape[0]])

def partialmethod(func, *frozen_args, **frozen_kwargs):
    """Wrap a method with partial application of given positional and keyword
    arguments.

    Parameters
    ----------
    func : callable
        A method to wrap.
    frozen_args : misc
        Fixed positional arguments.
    frozen_kwargs : misc
        Fixed keyword arguments.

    Returns
    -------
    method : callable
        Wrapped method.
    """
    @functools.wraps(func)
    def method(self, *args, **kwargs):
        """Wrapped method."""
        return func(self, *frozen_args, *args, **frozen_kwargs, **kwargs)
    return method

def seismic_plot(arrs, names=None, figsize=None, save_to=None, **kwargs):
    """Plot seismogram(s).

    Parameters
    ----------
    arrs : array-like
        Seismogram or sequence of seismograms to plot.
    names : str or array-like, optional
        Title names to identify subplots.
    figsize : array-like, optional
        Output plot size.
    save_to : str or None, optional
        If not None, save plot to given path.
    kwargs : dict
        Named argumets to matplotlib.pyplot.imshow

    Returns
    -------
    Plot of seismogram(s).
    """
    if np.asarray(arrs).ndim == 2:
        arrs = (arrs,)

    if isinstance(names, str):
        names = (names,)

    fig, ax = plt.subplots(1, len(arrs), figsize=figsize, squeeze=False)
    for i, arr in enumerate(arrs):
        ax[0, i].imshow(arr.T, **kwargs)
        if names is not None:
            ax[0, i].set_title(names[i])

        ax[0, i].set_aspect('auto')

    plt.show()

def spectrum_plot(frame, arrs, rate, max_freq=None, names=None,
                  figsize=None, save_to=None, **kwargs):
    """Plot seismogram(s) and power spectrum of given region in the seismogram(s).

    Parameters
    ----------
    frame : tuple
        List of slices that frame region of interest.
    arrs : array-like
        Seismogram or sequence of seismograms.
    rate : scalar
        Sampling rate.
    max_freq : scalar
        Upper frequence limit.
    names : str or array-like, optional
        Title names to identify subplots.
    figsize : array-like, optional
        Output plot size.
    save_to : str or None, optional
        If not None, save plot to given path.
    kwargs : dict
        Named argumets to matplotlib.pyplot.imshow

    Returns
    -------
    Plot of seismogram(s) and power spectrum(s).
    """
    if np.asarray(arrs).ndim == 2:
        arrs = (arrs,)

    if isinstance(names, str):
        names = (names,)

    fig, ax = plt.subplots(2, len(arrs), figsize=figsize, squeeze=False)
    for i, arr in enumerate(arrs):
        ax[0, i].imshow(arr.T, **kwargs)
        rect = patches.Rectangle((frame[0].start, frame[1].start),
                             frame[0].stop - frame[0].start,
                             frame[1].stop - frame[1].start,
                             edgecolor='r', facecolor='none', lw=2)
        ax[0, i].add_patch(rect)
        ax[0, i].set_title('Seismogram {}'.format(names[i] if names
                                                  is not None else ''))
        ax[0, i].set_aspect('auto')
        spec = abs(np.fft.rfft(arr[frame], axis=1))**2
        freqs = np.fft.rfftfreq(len(arr[frame][0]), d=timestep)
        mask = freqs <= max_freq if max_freq is not None else freqs
        ax[1, i].plot(freqs[mask], np.mean(spec, axis=0)[mask], lw=2)
        ax[1, i].set_xlabel('Hz')
        ax[1, i].set_title('Spectrum plot {}'.format(names[i] if names
                                                     is not None else ''))
        ax[1, i].set_aspect('auto')

    if save_to is not None:
        plt.savefig(save_to)

    plt.show()
