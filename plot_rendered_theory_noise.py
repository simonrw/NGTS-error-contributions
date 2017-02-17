#!/usr/bin/env python

import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
    parser = argparse.ArgumentParser();
    parser.add_argument('-d', '--dark', required=True)
    parser.add_argument('-b', '--bright', required=True)
    parser.add_argument('-o', '--output', required=True)
    args = parser.parse_args()

    fig_width = 5
    fig_height = fig_width / 1.3

    plt.rc('figure', figsize=(fig_width, fig_height))
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif',
        serif='Times, Palatino, New Century Schoolbook, Bookman, Computer Modern Roman', monospace='Courier, Computer Modern Typewriter')


    dark = pd.read_csv(args.dark)
    bright = pd.read_csv(args.bright)

    colours = {
        'dark_total': 'k',
        'bright_total': 'k',
        'sky': 'b',
        'scintillation': 'c',
        'source': 'r',
        'read': 'g',
        }

    fig, axis = plt.subplots()

    axis.semilogy(dark['magnitude'], dark['read'], '-', label='Read',
                color=colours['read'])
    axis.semilogy(dark['magnitude'], dark['sky'], '-', label='Dark Sky',
                color=colours['sky'])
    axis.semilogy(dark['magnitude'], dark['scintillation'], '-',
                label='Scintillation', color=colours['scintillation'])
    axis.semilogy(dark['magnitude'], dark['source'], '-', label='Source',
                color=colours['source'])
    axis.semilogy(dark['magnitude'], dark['total'], '-',
                label='Dark total', color=colours['dark_total'])
    axis.semilogy(bright['magnitude'], bright['total'], ':',
                label='Bright total', color=colours['bright_total'])


    axis.set(
        xlim=(18, 8),
        ylim=(1E-5, 1E-1),
        xlabel='I magntiude',
        ylabel='Noise',
        )
    axis.grid(True, which='both')
    axis.legend(loc='best')
    fig.tight_layout()

    fig.savefig(args.output)
