from typing import Tuple, NamedTuple
import matplotlib.pyplot as plt
import matplotlib as mpl

import numpy as np
from temgymbasic.components import DoubleDeflector, Lens, Sample, Detector, Biprism, Aperture, \
                                   Deflector, XAxialBeam, RadialSpikesBeam


class PlotParams(NamedTuple):
    num_rays: int = 512
    ray_color: str = 'dimgray'
    fill_color: str = 'aquamarine'
    fill_color_pair: Tuple[str, str] = ('khaki', 'deepskyblue')
    fill_alpha: float = 1.
    ray_alpha: float = 1.
    component_lw: float = 1.
    edge_lw: float = 1.
    ray_lw: float = 0.01
    label_fontsize: int = 12
    figsize: Tuple[int, int] = (6, 12)
    extent_scale: float = 1.3


def plot_model(model, *, plot_params: PlotParams = PlotParams()):
    p = plot_params
    rays = tuple(model.run_iter(num_rays=p.num_rays))
    if isinstance(model.components[0], XAxialBeam):
        raise NotImplementedError
    if isinstance(model.components[0], RadialSpikesBeam):
        raise NotImplementedError
    x = np.stack(tuple(r.x for r in rays), axis=0)
    z = np.asarray(tuple(r.z for r in rays))
    min_x_idx = np.argmin(x[0, :])
    max_x_idx = np.argmax(x[0, :])
    aspect = p.figsize[1]/p.figsize[0]
    detector_size_x = model.detector.pixel_size * model.detector.shape[1]

    extent = p.extent_scale*np.max(x)

    fig, ax = plt.subplots(figsize=p.figsize)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(color='lightgrey', linestyle='--', linewidth=0.5)
    ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    ax.set_yticks([])
    ax.set_yticklabels([])
    ax.get_xaxis().set_ticks(
        [-detector_size_x/2, 0, detector_size_x/2])
    ax.set_xlim([-detector_size_x, detector_size_x])
    ax.set_ylim([model.components[-1].z, model.components[0].z])
    ax.text(x[0, max_x_idx], model.components[0].z, model.components[0].name,
            fontsize=p.label_fontsize, zorder=1000)
    ax.plot(x, z,
        color=p.ray_color, linewidth=p.ray_lw, alpha=p.ray_alpha, zorder=1)
    ax.fill_betweenx(z, x[:, min_x_idx], x[:, max_x_idx],
                color=p.fill_color, edgecolor=p.fill_color, zorder=0, alpha=p.fill_alpha, lw=None)
    ax.plot(x[:, min_x_idx], z,
        color=p.ray_color, linewidth=p.edge_lw, alpha=p.ray_alpha, zorder=1)
    ax.plot(x[:, max_x_idx], z,
        color=p.ray_color, linewidth=p.edge_lw, alpha=p.ray_alpha, zorder=1)

    for component in model.components:
        if isinstance(component, DoubleDeflector):
            radius = -detector_size_x/2
            ax.text(extent, component.first.z, component.first.name + ' ' + component.name,
                    fontsize=p.label_fontsize, va='bottom', zorder=1000)
            ax.plot([-radius, 0], [component.first.z, component.first.z],
                    color='lightcoral', alpha=1, linewidth=p.component_lw, zorder=999)
            ax.plot([0, radius], [component.first.z, component.first.z],
                    color='lightblue', alpha=1, linewidth=p.component_lw, zorder=999)
            ax.plot([-radius, radius], [component.first.z, component.first.z],
                    color='k', alpha=0.8, linewidth=p.component_lw+2, zorder=998)
            ax.text(extent, component.second.z, component.second.name + ' ' + component.name,
                    fontsize=p.label_fontsize, va='bottom', zorder=1000)
            ax.plot([-radius, 0], [component.second.z, component.second.z],
                    color='lightcoral', alpha=1, linewidth=p.component_lw, zorder=999)
            ax.plot([0, radius], [component.second.z, component.second.z],
                    color='lightblue', alpha=1, linewidth=p.component_lw, zorder=999)
            ax.plot([-radius, radius], [component.second.z, component.second.z],
                    color='k', alpha=0.8, linewidth=p.component_lw+2, zorder=998)
        if isinstance(component, Deflector):
            radius = -detector_size_x/2
            ax.text(extent, component.z, component.name, fontsize=p.label_fontsize,
                    va='bottom', zorder=1000)
            ax.plot([-radius, 0], [component.z, component.z],
                    color='lightcoral', alpha=1, linewidth=p.component_lw, zorder=999)
            ax.plot([0, radius], [component.z, component.z],
                    color='lightblue', alpha=1, linewidth=p.component_lw, zorder=999)
            ax.plot([-radius, radius], [component.z, component.z],
                    color='k', alpha=0.8, linewidth=p.component_lw+2, zorder=998)
        elif isinstance(component, Lens):
            radius = -detector_size_x
            ax.text(extent, component.z, component.name, fontsize=p.label_fontsize,
                    va='bottom', zorder=1000)
            ax.add_patch(mpl.patches.Arc((0, component.z), radius, height=0.03/aspect,
                                        theta1=0, theta2=180, linewidth=1,
                                        fill=False, zorder=999, edgecolor='k'))
            ax.add_patch(mpl.patches.Arc((0, component.z), radius, height=0.03/aspect,
                                        theta1=180, theta2=0, linewidth=1,
                                        fill=False, zorder=-1, edgecolor='k'))
        elif isinstance(component, Sample):
            ax.text(extent, component.z,
                component.name, fontsize=p.label_fontsize, zorder=1000, va='bottom')
            wx = model.sample.scan_step_yx[1]*model.sample.scan_shape[1]
            ax.plot([0-wx/2, 0+wx/2], [component.z, component.z],
                color='dimgrey', alpha=0.8, linewidth=3)
        elif isinstance(component, Detector):
            ax.text(extent, component.z, component.name, fontsize=p.label_fontsize,
                    zorder=1000, va='bottom')
            ax.plot([-detector_size_x/2, detector_size_x/2],
                    [component.z, component.z], color='dimgrey',
                    zorder=1000, alpha=1, linewidth=5)
        elif isinstance(component, Biprism):
            raise NotImplementedError
        elif isinstance(component, Aperture):
            raise NotImplementedError

    return fig, ax
