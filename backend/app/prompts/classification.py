"""Algorithm-specific instructions for classification notes."""

CLASSIFICATION_ALGORITHM_NAMES = {
    "logistic_regression": "Logistic Regression",
    "decision_tree": "Decision Tree",
    "random_forest": "Random Forest",
    "svm": "Support Vector Machine (SVM)",
    "naive_bayes": "Naive Bayes",
    "knn": "K-Nearest Neighbors (KNN)",
}

CLASSIFICATION_ALGORITHM_INSTRUCTIONS = {
    "logistic_regression": """Cover binary and multiclass logistic regression,
the sigmoid function, odds and log-odds, decision boundaries, coefficient
interpretation, loss function, regularization, and key assumptions. Distinguish
logistic regression from linear regression and explain when it is appropriate.""",
    "decision_tree": """Cover the tree structure, splitting criteria such as
Gini impurity and entropy, information gain, stopping criteria, pruning,
overfitting, interpretability, and how predictions are made.""",
    "random_forest": """Cover bagging, bootstrap samples, random feature
selection, aggregation by majority vote, out-of-bag evaluation, feature
importance, strengths over a single decision tree, and practical limitations.""",
    "svm": """Cover maximum-margin classification, support vectors, the
soft-margin parameter C, hinge loss, kernel intuition, common kernels,
feature scaling, multiclass strategies, and limitations on large datasets.""",
    "naive_bayes": """Cover Bayes' theorem, conditional independence, priors
and likelihoods, posterior prediction, Gaussian, Multinomial, and Bernoulli
variants, smoothing, common use cases, and limitations of the assumption.""",
    "knn": """Cover distance-based classification, choosing k, majority vote,
distance metrics, feature scaling, the bias-variance trade-off, prediction
cost, curse of dimensionality, and practical limitations.""",
}
