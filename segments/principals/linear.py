"""
Module principals
"""

import numpy as np
import pandas as pd
import sklearn.decomposition

import collections

import segments.functions.margin


# noinspection PyUnresolvedReferences,PyProtectedMember
class Linear:
    """
    Class Principals
    """

    def __init__(self):
        """
        The constructor
        """

        self.LPCA = collections.namedtuple(typename='LPCA', field_names=['projections', 'variance'])

        self.margin = segments.functions.margin.Margin()
        self.random_state = 5

    @staticmethod
    def variance(model: sklearn.decomposition.PCA) -> pd.DataFrame:
        """
        The dimensionality reduction model; PCA.

        :param model: The PCA projections

        :return:
        """

        discrete = model.explained_variance_ratio_
        explain = discrete.cumsum()
        components = np.arange(start=1, stop=1 + model.n_components_)
        return pd.DataFrame(data={'components': components, 'explain': explain,
                                  'discrete': discrete})

    @staticmethod
    def projections(reference: np.ndarray, transform: np.ndarray, limit: int, identifiers: list) -> pd.DataFrame:

        # The critical components
        core = transform[:, :limit].copy()

        # Fields
        fields = ['C{:02d}'.format(i) for i in np.arange(1, 1 + limit)]
        fields = identifiers + fields

        # values
        values = np.concatenate((reference, core), axis=1)

        return pd.DataFrame(data=values, columns=fields)

    def exc(self, data: pd.DataFrame, exclude: list, identifiers: list) -> collections.namedtuple:
        """

        :param data:
        :param exclude:
        :param identifiers:
        :return:
        """

        # The independent variables
        regressors = data.columns.drop(labels=exclude)

        # Decomposition
        pca = sklearn.decomposition.PCA(n_components=None, svd_solver='full', random_state=self.random_state)
        model: sklearn.decomposition.PCA = pca.fit(data[regressors])

        # The transform
        transform = model.fit_transform(data[regressors])

        # The variance explained by the decomposition components
        variance: pd.DataFrame = self.variance(model=model)

        # Hence, plausible number of core principal components
        index: int = self.margin.exc(values=variance.discrete.values)
        limit = variance.components[index]

        # Projections
        reference = data[identifiers].values.reshape(data.shape[0], len(identifiers))
        projections = self.projections(reference=reference, transform=transform, limit=limit, identifiers=identifiers)

        return self.LPCA._make((projections, variance))