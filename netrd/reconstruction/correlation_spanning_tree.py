"""
correlation_spanning_tree.py
--------------

Graph reconstruction algorithm based on Mantegna, R. N. (1999). Hierarchical structure in
financial markets. The European Physical Journal B-Condensed Matter and Complex Systems,
11(1), 193-197. DOI https://doi.org/10.1007/s100510050929
https://link.springer.com/article/10.1007/s100510050929

author: Matteo Chinazzi
Submitted as part of the 2019 NetSI Collabathon.
"""

from .base import BaseReconstructor
import numpy as np
import networkx as nx
from scipy.sparse.csgraph import minimum_spanning_tree


class CorrelationSpanningTree(BaseReconstructor):
    def fit(self, TS, distance='root_inv', **kwargs):
        r"""Create a minimum spanning tree connecting the sensors.

        The empirical correlation matrix is used to first compute a
        distance matrix and then to create a minimum spanning tree
        connecting all the sensors in the data.  This method implements the
        methodology described in [1] and applied in the context of creating
        a graph connecting the stocks of a portfolio of generated by
        looking at the correlations between the daily time series of stock
        prices.

        The results dictionary also stores the distance matrix (computed
        from the correlations) as `'distance_matrix'`.

        Parameters
        ----------

        TS (np.ndarray)
            :math:`N \times L` array consisting of :math:`L` observations
            from :math:`N` sensors.

        distance (str)
            'inv_square' calculates distance as :math:`1-corr_{ij}^2`
            (Mantegna 1999). 'root_inv' calculates distance as
            :math:`\sqrt{2 (1-corr_{ij})}` (Bonanno et al. 2003).

        Returns
        -------

        G (nx.Graph)
            A reconstructed graph with :math:`N` nodes.

        Examples
        --------
        .. code:: python

            import numpy as np
            import networkx as nx
            from matplotlib import pyplot as plt
            from netrd.reconstruction import CorrelationSpanningTree

            N = 25
            T = 300
            M = np.random.normal(size=(N,T))

            print('Create correlated time series')
            market_mode = 0.4*np.random.normal(size=(1,T))
            M += market_mode

            sector_modes = {d: 0.5*np.random.normal(size=(1,T)) for d in range(5)}
            for sector_mode, vals in sector_modes.items():
                M[sector_mode*5:(sector_mode+1)*5,:] += vals

            print('Link node colors to sectors')
            colors = ['b','r','g','y','m']
            node_colors = [color for color in colors for __ in range(5)]


            print('Network reconstruction step')
            cst_net = CorrelationSpanningTree()
            G = cst_net.fit(M)

            print('Plot reconstructed spanning tree')
            fig, ax = plt.subplots()
            nx.draw(G, ax=ax, node_color=node_colors)


        References
        ----------

        [1] Mantegna, R. N. (1999). Hierarchical structure in financial markets.
        The European Physical Journal B-Condensed Matter and Complex Systems, 11(1), 193-197.
        DOI https://doi.org/10.1007/s100510050929
        https://link.springer.com/article/10.1007/s100510050929

        [2] Bonanno, G., Caldarelli, G., Lillo, F. & Mantegna, R. N. (2003)
        Topology of correlation-based minimal spanning trees in real and model markets.
        Physical Review E 68.

        [3] Vandewalle, N., Brisbois, F. & Tordoir, X. (2001)
        Non-random topology of stock markets. Quantitative Finance 1, 372–374.

        """
        N, L = TS.shape

        C = np.corrcoef(TS)  # Empirical correlation matrix

        D = (
            np.sqrt(2 * (1 - C)) if distance == 'root_inv' else 1 - np.square(C)
        )  # Distance matrix

        self.results['distance_matrix'] = D

        MST = minimum_spanning_tree(D)  # Minimum Spanning Tree

        G = nx.from_scipy_sparse_matrix(MST)

        self.results['graph'] = G

        return G
