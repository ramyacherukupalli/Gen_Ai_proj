"""Fixed evaluation cases used by every prompt-comparison run."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    """A stable study-notes request and concepts expected in its response."""

    algorithm: str
    algorithm_name: str
    difficulty: str
    notes_format: str
    expected_concepts: tuple[str, ...]


ALGORITHMS = (
    ("logistic_regression", "Logistic Regression", ("sigmoid", "log-odds", "regularization")),
    ("decision_tree", "Decision Tree", ("gini", "entropy", "pruning")),
    ("random_forest", "Random Forest", ("bagging", "bootstrap", "out-of-bag")),
    ("svm", "Support Vector Machine", ("margin", "support vectors", "kernel")),
    ("naive_bayes", "Naive Bayes", ("bayes", "conditional independence", "prior")),
    ("knn", "K-Nearest Neighbors", ("distance", "k", "feature scaling")),
)

EVALUATION_CASES = tuple(
    EvaluationCase(
        algorithm=algorithm,
        algorithm_name=algorithm_name,
        difficulty=difficulty,
        notes_format="detailed",
        expected_concepts=concepts,
    )
    for algorithm, algorithm_name, concepts in ALGORITHMS
    for difficulty in ("beginner", "intermediate", "advanced")
)
