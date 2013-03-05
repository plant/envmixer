"""
studies/crowdflower/baryplot.py
natural-mixer

2013 Brandon Mechtley
Arizona State University

Plot results from CrowdFlower study reports.

Usage: python baryplot.py
"""

import argparse
import json

import numpy as np
import matplotlib as mpl

mpl.use('ps')
mpl.rc('text',usetex=True)
mpl.rc('text.latex', preamble='\usepackage[usenames,dvipsnames]{xcolor}')
mpl.rc('font', family='Times serif', style='normal', weight='medium')

import matplotlib.pyplot as pp

from pybatchdict import *
from barycentric import *

def makedict(fn):
    mapping = open(fn, 'r')
    
    sounds = {}
    
    for line in mapping:
        (filename, filehash) = line.rstrip('\n').split(', ')
        tokens = filename.split('.wav')[0].split('-')
        stype = tokens[1]
        pos = '-'.join(tokens[2:5])
        iteration = tokens[0] if stype == 'source' else tokens[5]
     
        if stype not in sounds:
            sounds[stype] = {}
    
        if pos not in sounds[stype]:
            sounds[stype][pos] = {}

        sounds[stype][pos][iteration] = filehash
    
    return sounds

def circumcircle(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    ax2, ay2, bx2, by2, cx2, cy2 = [d ** 2 for d in [ax, ay, bx, by, cx, cy]]

    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

    ux = (
        (ax2 + ay2) * (by - cy) + \
        (bx2 + by2) * (cy - ay) + \
        (cx2 + cy2) * (ay - by)
    ) / d

    uy = (
        (ax2 + ay2) * (cx - bx) + \
        (bx2 + by2) * (ax - cx) + \
        (cx2 + cy2) * (bx - ax)
    ) / d

    return ux, uy

def voronoi(x, y):
    p = np.array(zip(x, y))
    d = mpl.tri.Triangulation(x, y)
    t = d.triangles
    n = t.shape[0]

    # Get circle for each triangle, center will be a voronoi cell point
    cells = [list() for i in range(x.size)]

    for i in range(n):
        v = [p[t[i,j]] for j in range(3)]
        pt = circumcircle(v[0], v[1], v[2])
        
        cells[t[i,0]].append(pt)
        cells[t[i,1]].append(pt)
        cells[t[i,2]].append(pt)

    # Reordering cell p in trigonometric way
    for i, cell in enumerate(cells):
        xy = np.array(cell)
        order = np.argsort(np.arctan2(xy[:,1] - y[i], xy[:,0] - x[i]))

        cell = xy[order].tolist()
        cell.append(cell[0])

        cells[i] = cell

    return cells, d.triangles

def unique_rows(a):
    '''Return only unique rows from an array.
        a: np.array
            input array'''

    return np.array([np.array(x) for x in set(tuple(x) for x in a)])

def baryplot(values, points=[], 
    labels='abc', cmap=mpl.cm.RdYlGn, clabel=''
):
    p = bary2cart(points) if len(points) else bary2cart(lattice(3))
    values = (values - np.amin(values)) / (np.amax(values) - np.amin(values))
    cells, triangles = voronoi(p[:,0], p[:,1])

    xmin, xmax, xavg = np.amin(p[:,0]), np.amax(p[:,0]), np.mean(p[:,0])
    ymin, ymax, yavg = np.amin(p[:,1]), np.amax(p[:,1]), np.mean(p[:,1])

    s60, c60 = np.sin(np.pi / 3.), np.cos(np.pi / 3.)
    s30, c30 = np.sin(np.pi / 6.), np.cos(np.pi / 6.)
    
    # Start drawing.
    ax = pp.gca()

    # Clipping triangle for the voronoi patches.
    clip = mpl.patches.Polygon([
        (xmin, ymin), (xmax, ymin), (xavg, ymax),
    ], transform=ax.transData)
    
    # Draw voronoi patches.
    for i, cell in enumerate(cells):
        codes = [mpl.path.Path.MOVETO] \
            + [mpl.path.Path.LINETO] * (len(cell) - 2) \
            + [mpl.path.Path.CLOSEPOLY]
        
        print cell
        pth = mpl.path.Path(cell, codes)
        
        patch = mpl.patches.PathPatch(
            pth, 
            zorder=-1, 
            facecolor=cmap(values[i]),
            clip_path=clip,
            edgecolor='none'
        )

        ax.add_patch(patch)
    
    # Add barycentric labels for vertices.
    ax.text(xmin - .0125, ymin - .02, '$(0,1,0)$', ha='right', va='center')
    ax.text(xmax + .0125, ymin - .02, '$(0,0,1)$', ha='left', va='center')
    ax.text(xavg, ymax + .035, '$(1,0,0)$', ha='center', va='bottom')
    
    # Labels.
    ax.text(
        xavg + c30 * .325, yavg + s30 * .325, 
        labels[2], ha='center', va='center', rotation=-60
    )
    
    ax.text(
        xavg, ymin - .05, 
        labels[1], ha='center', va='top'
    )
    
    ax.text(
        xavg - c30 * .325, yavg + s30 * .325, 
        labels[0], ha='center', va='center', rotation=60
    )

    arrowopts = dict(
        width=.00125,
        frac=.0125,
        headwidth=.01,
        transform=ax.transData
    )

    fig = pp.gcf()

    # Arrows along edges.
    ax.add_patch(mpl.patches.YAArrow(
        fig,
        (xmin - c60 * .025, ymin + s60 * .025),
        (xavg - c60 * .025, ymax + s60 * .025),
        **arrowopts
    ))
    
    ax.add_patch(mpl.patches.YAArrow(
        fig,
        (xmax, ymin - .025),
        (xmin, ymin - .025),
        **arrowopts
    ))
    
    ax.add_patch(mpl.patches.YAArrow(
        fig,
        (xavg + c60 * .025, ymax + s60 * .025),
        (xmax + c60 * .025, ymin + s60 * .025),
        **arrowopts
    ))
    
    # Make axes equal, get rid of border.
    pp.axis('equal')
    ax.axis([
        xmin - c60 * .2, xmax + c60 * .2, 
        ymin - s60 * .2, ymax + s60 * .2
    ])
    pp.axis('off')

    norm = mpl.colors.Normalize(vmin=np.amin(values), vmax=np.amax(values))
    cax, kw = mpl.colorbar.make_axes(ax, orientation='vertical', shrink=0.7)
    cb = mpl.colorbar.ColorbarBase(
        cax, 
        cmap=cmap, 
        norm=norm, 
        orientation='vertical',
        ticks=[0.0, 0.5, 1.0]
    )
    
    cb.set_label(clabel)

def aggregate_result(json, coordmapping, resultpath):
    keyname = resultpath.split('/')[-1]
    aggdict = {}

    for result in json:
        jsondict = coordmapping[result['data']['s0']]

        if jsondict['type'] != 'source':
            posstr = '%.2f,%.2f,%.2f' % jsondict['pos']
            aggdict.setdefault(posstr, [])

            for judgment in result['results']['judgments']:
                if not judgment['rejected']:
                    value = float(getkeypath(judgment, resultpath))
                    aggdict[posstr].append(value)

    return aggdict

if __name__ == '__main__':
    # 
    # 1. Command-line arguments.
    # 

    parser = argparse.ArgumentParser(
        description='Make plots for a CrowdFlower results batch.'
    )
    
    parser.add_argument(
        'mapping', metavar='mapping', default='mapping.txt', type=str, 
        help='CSV input file. See makemapping.sh for more information.'
    )
    
    parser.add_argument(
        'json', metavar='json', default='results.json', 
        type=str, help='JSON results file from CrowdFlower.'
    )

    args = parser.parse_args()
    
    #
    # 2. Load/manipulate JSON.    
    #

    jsonfile = open(args.json)
    jsondata = json.loads('[' + ','.join([line for line in jsonfile]) + ']')
    jsonfile.close()

    # Map coords to file hashes.
    mapping = makedict(args.mapping)

    # Convert to {filehash: {'pos': (a, b, c), 'type': t}}
    # where type is 'source' or 'naive'
    coordmapping = {}
    for stype in mapping:
        for sloc in mapping[stype]:
            a, b, c = [float(d) for d in sloc.split('-')]
            
            for source in mapping[stype][sloc]:
                coordmapping[mapping[stype][sloc][source]] = {
                    'pos': (a, b, c),
                    'type': stype
                }

    # Aggregate data.
    agg = aggregate_result(
        jsondata, coordmapping, 
        '/data/test_clip_perceptual_convincingness'
    )
    
    #
    # 3. Plots.
    #

    points = lattice(3)
    labels = [r'$S_{DB}$', r'$S_{SG}$', r'$S_{DC}$']
    
    # Plot mean perceptual convincingness.
    pp.figure(figsize=(4, 2.5))
    pp.title('Naive model: perceptual convincingness')
    
    baryplot(
        [
            np.mean(agg[','.join([
                '%.2f' % a for a in p])
            ])
        ],
        points=points,
        labels=labels,
        clabel='convincingness'
    )

    pp.savefig('realism.eps')

    # Plot perceptual convincingness variance.
    pp.figure(figsize=(4, 2.5))

    baryplot(
        [
            np.var(agg[','.join([
                '%.2f' % a for a in p
            ])])
            for p in points
        ], 
        points=points, 
        labels=labels, 
        clabel='variance'
    )

    pp.savefig('variance.eps')

    