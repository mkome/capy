#!/usr/bin/env python
# coding: utf-8

import requests 
import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import math

FACET_STATS = 'facet_stats'
DIMS = 'dims'
STATS = 'stats'
ID = 'id'
CORRELATION = 'correlation'
FREQUENCY = 'count'
CORRELATION_LABEL = 'Correlation'
    
class CAClient:
    
    def __init__(self, endpoint):
        self.endpoint = endpoint
        
    def stats(self, response, statsName, dimName):
        fs = response.json()[FACET_STATS]
        labels = list(map(lambda i: i[ID], fs[DIMS][dimName]))
        correlation = list(map(lambda i: i[CORRELATION], fs[STATS][statsName][dimName]))
        frequency = list(map(lambda i: i[FREQUENCY], fs[STATS][statsName][dimName]))
        return {dimName:labels, FREQUENCY:frequency, CORRELATION:correlation}
    
    def matrix(self, response, statsName, row, column):
        fs = response.json()[FACET_STATS]
        rowLabels = list(map(lambda i: i[ID], fs[DIMS][row]))
        columnLabels = list(map(lambda i: i[ID], fs[DIMS][column]))
        
        correlation = list(
            map(lambda r : list(map(lambda c : c[CORRELATION], r)), 
                list(map(lambda r : r[column], fs[STATS][statsName][row]))
            )
        )
        frequency = list(
            map(lambda r : list(map(lambda c : c[FREQUENCY], r)), 
            list(map(lambda r : r[column], fs[STATS][statsName][row]))
            )
        )
        return {row:rowLabels, column:columnLabels, FREQUENCY:frequency, CORRELATION:correlation}
    
    def facets(self, field, query, limit=100):
        return self.stats(requests.get(self.endpoint,
                           params={
                                "facet.field":field,
                                "facet.limit":limit,
                                "facet":"true",
                                "q":query,
                                "q.op":"AND",
                                "rows":"0",
                                "facet.stats":"default"
                                }), field, field)
    
    def ranges(self, field, query, start, end, gap):
        return self.stats(requests.get(self.endpoint,
                           params={
                                "facet.range":field,
                                "facet.range.start":start,
                                "facet.range.end":end,
                                "facet.range.gap":gap,
                                "facet":"true",
                                "q":query,
                                "q.op":"AND",
                                "rows":"0",
                                "facet.stats":"default"
                                }), field, field)
    
    def pairs(self, row, column, query, rowLimit=100, columnLimit=100):
        response = requests.get(self.endpoint, 
                            params={
                                "facet.field":[row, column],
                                "facet":"true",
                                "q":query,
                                "q.op":"AND",
                                "rows":"0",
                                "facet.stats":"pairs",
                                "f." + row + ".facet.limit":rowLimit,
                                "f." + column + ".facet.limit":columnLimit,
                                }
                           )
        return self.matrix(response, 'pairs', row, column)
    
    def heatmap(self, field, query, box, level):
        response = requests.get(self.endpoint, 
                            params={
                                "facet.heatmap":field,
                                "facet":"true",
                                "q":query,
                                "q.op":"AND",
                                "rows":"0",
                                "facet.stats":"default",
                                "facet.heatmap.gridLevel":level,
                                "facet.heatmap.geom":box 
                                }
                           )
        return self.matrix(response, 'heatmap', field + '_vertical', field + '_horizontal')
    
    def showFacet(self, query, fields, n=10, limit=100, figsize=(10,5), vertical=False, shareXY=False):
        d1 = fields[0][0]
        l1 = fields[0][1]
        
        f1 = pd.DataFrame(self.facets(d1, query)).sort_values(by=CORRELATION, ascending=False)
        size = len(fields)
        
        if vertical:
            f, (ax1) = plt.subplots(1, 1, figsize=figsize, sharex=shareXY)
            sns.barplot(y=d1, x=CORRELATION, data=f1.head(n), color="b", ax=ax1)
            ax1.set(ylabel=l1, xlabel=CORRELATION_LABEL)
        else:
            f, (ax1) = plt.subplots(1, 1, figsize=figsize, sharey=shareXY)
            sns.barplot(x=d1, y=CORRELATION, data=f1.head(n), color="b", ax=ax1)
            ax1.set(xlabel=l1, ylabel=CORRELATION_LABEL)
            
    def showFacets(self, query, fields, n=10, limit=100, figsize=(10,10), vertical=False, shareXY=False):
        d1 = fields[0][0]
        d2 = fields[1][0]
        d3 = fields[2][0]
        l1 = fields[0][1]
        l2 = fields[1][1]
        l3 = fields[2][1]
        
        f1 = pd.DataFrame(self.facets(d1, query)).sort_values(by=CORRELATION, ascending=False)
        f2 = pd.DataFrame(self.facets(d2, query)).sort_values(by=CORRELATION, ascending=False)
        f3 = pd.DataFrame(self.facets(d3, query)).sort_values(by=CORRELATION, ascending=False)
        size = len(fields)
        
        if vertical:
            f, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figsize, sharex=shareXY)
            sns.barplot(y=d1, x=CORRELATION, data=f1.head(n), color="b", ax=ax1)
            ax1.set(ylabel=l1, xlabel=CORRELATION_LABEL)
            sns.barplot(y=d2, x=CORRELATION, data=f2.head(n), color="b", ax=ax2)
            ax2.set(ylabel=l2, xlabel=CORRELATION_LABEL)
            sns.barplot(y=d3, x=CORRELATION, data=f3.head(n), color="b", ax=ax3)
            ax3.set(ylabel=l3, xlabel=CORRELATION_LABEL)
        else:
            f, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=figsize, sharey=shareXY)
            sns.barplot(x=d1, y=CORRELATION, data=f1.head(n), color="b", ax=ax1)
            ax1.set(xlabel=l1, ylabel=CORRELATION_LABEL)
            sns.barplot(x=d2, y=CORRELATION, data=f2.head(n), color="b", ax=ax2)
            ax2.set(xlabel=l2, ylabel=CORRELATION_LABEL)
            sns.barplot(x=d3, y=CORRELATION, data=f3.head(n), color="b", ax=ax3)
            ax3.set(xlabel=l3, ylabel=CORRELATION_LABEL)
   
    def showRanges(self, query, fields, figsize=(10,10)):
        d1 = fields[0][0]
        d2 = fields[1][0]
        l1 = fields[0][1]
        l2 = fields[1][1]
        s1 = fields[0][2]
        s2 = fields[1][2]
        e1 = fields[0][3]
        e2 = fields[1][3]
        i1 = fields[0][4]
        i2 = fields[1][4]
        
        # Set up figure
        f, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, sharey=True)
        
        # Retrieve correlations
        f1 = pd.DataFrame(self.ranges(d1, query, s1, e1, i1))
        f2 = pd.DataFrame(self.ranges(d2, query, s2, e2, i2))
        
        # Draw State, Year and Miles
        sns.barplot(data=f1, x=d1, y=CORRELATION, color="b", ax=ax1)
        ax1.set(xlabel=l1, ylabel=CORRELATION_LABEL)
        sns.barplot(data=f2, x=d2, y=CORRELATION, color="b", ax=ax2)
        ax2.set(xlabel=l2, ylabel=CORRELATION_LABEL)        
    
    def showFacetPairs(self, query, x, y, xlimit=10, ylimit=10, figsize=(10,10)):
        dx = x[0]
        dy = y[0]
        lx = x[1]
        ly = y[1]
        # Set up figure
        f, ax = plt.subplots(1, 1, figsize=figsize)
        
        # Retrieve correlations
        df = self.pairs(dx, dy, query, xlimit, ylimit)
        sns.heatmap(np.array(df[CORRELATION]), xticklabels=df[dy], yticklabels=df[dx], cbar=False, cmap='Blues')
        ax.set(xlabel=ly, ylabel=lx)
        
    def showHeatmap(self, query, field, box, level=1, figsize=(10,10)):
        # Set up figure
        f, ax = plt.subplots(1, 1, figsize=figsize)
        
        # Retrieve correlations
        df = self.heatmap(field, query, box, level)
        sns.heatmap(np.array(df[CORRELATION]), xticklabels=df[field + '_horizontal'], yticklabels=df[field + '_vertical'], cbar=False, cmap='Blues')
  

    def getGeoHeatmapData(self, query, field, box, level):
        df = self.heatmap(field, query, box, level);
        corr = np.array(df['correlation'])
        mul = math.pow(10, math.ceil(math.fabs(math.log10(np.min(corr[np.nonzero(corr)])))))
        m = (corr * mul).astype(int)
        data = np.empty((0,2), float)
        for (x,y), value in np.ndenumerate(m):
            if value == 0:
                continue
            step = math.ceil(math.sqrt(value))
            x0, x1 = [float(x) for x in df[field + '_vertical'][x].split(', ')]
            y0, y1 = [float(y) for y in df[field + '_horizontal'][y].split(', ')]
            xv, yv = np.meshgrid(np.linspace(x0, x1, step), np.linspace(y0, y1, step))
            positions = np.vstack((xv.ravel(), yv.ravel())).T
            data = np.append(data, positions, axis=0)
        return data.tolist()       
