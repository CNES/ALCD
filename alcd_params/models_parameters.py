from typing import Literal, Optional
from pydantic import BaseModel


class LibSVMConfig(BaseModel):
    """
    Configuration parameters for the LibSVM model of OTB.

    Attributes
    ----------
    k : str
        Kernel type for the SVM (e.g., "linear").
    m : str
        Model type for the SVM (e.g., "csvc").
    c : str
        Cost parameter for the SVM (e.g., "1").
    opt : str
        Optimization flag, specifying whether optimization is enabled ("true"/"false").
    prob : str
        Probability estimates flag ("true"/"false").
    """
    k: Literal["linear", "rbf", "poly", "sigmoid"]
    m: Literal["csvc", "nusvc", "oneclass"]
    c: int
    opt: str
    prob: str
    rand : int


class BoostConfig(BaseModel):
    """
    Configuration parameters for the Boost model of OTB.

    Attributes
    ----------
    t : str
        Boosting type (e.g., "real").
    w : str
        Weak count.
    r : str
        Weight Trim Rate.
    m : str
        Maximum depth of the boost model.
    """
    t: Literal["discrete", "real", "logit", "gentle"]
    w: int
    r: float
    m: int
    rand : int


class DTConfig(BaseModel):
    """
    Configuration parameters for the Decision Tree (DT) model of OTB.

    Attributes
    ----------
    max : str
        Maximum depth of the decision tree.
    min : str
        Minimum samples required to split an internal node.
    ra : str
        Regularization amount.
    cat : str
        Number of categories in categorical features.
    f : str
        Maximum number of features to consider for splits.
    r : str
        Flag indicating randomization ("true"/"false").
    t : str
        Flag for additional tree configuration ("true"/"false").
    """
    max: int
    min: int
    ra: float
    cat: int
    f: int
    r: str
    t: str
    rand : int


class GBTConfig(BaseModel):
    """
    Configuration parameters for the Gradient Boosted Trees (GBT) model of OTB.

    Attributes
    ----------
    w : str
        Number of boosting iterations.
    s : str
        Regularization parameter
    p : str
        Portion of the whole training set used for each algorithm iteration
    max : str
        Maximum depth of the tree.
    """
    w: str
    s: str
    p: str
    max: str
    rand : int


class ANNConfig(BaseModel):
    """
    Configuration parameters for the Artificial Neural Network (ANN) model of OTB.

    Attributes
    ----------
    t : str
        Type of neural network (e.g., "reg" for regression).
    sizes : int
        Size of the hidden layers.
    f : str
        Activation function (e.g., "sig" for sigmoid).
    a : float
        Alpha regularization parameter.
    b : str
        Beta regularization parameter.
    bpdw : str
        Strength of the weight gradient term in the BACKPROP method
    bpms : str
        Strength of the momentum term (the difference between weights on the 2 previous iterations)
    rdw : float
        Initial value Delta_0 of update-values Delta_{ij} in RPROP method
    rdwm : str
        Update-values lower limit Delta_{min} in RPROP method.
    term : str
        Termination criteria [iter/eps/all].
    eps : float
        Epsilon value used in the Termination criteria.
    iter : int
        Maximum number of iterations used in the Termination criteria.
    """
    t: Literal["back", "reg"]
    sizes: int
    f: Literal["ident", "sig", "gau"]
    a: float
    b: float
    bpdw: float
    bpms: float
    rdw: float
    rdwm: float
    term: Literal["iter", "eps", "all"]
    eps: float
    iter: int
    rand : int


class RFConfig(BaseModel):
    """
    Configuration parameters for the Random Forest (RF) model of OTB.

    Attributes
    ----------
    max : int
        Maximum depth of the forest.
    min : int
        Minimum number of samples in each node.
    ra : float
        Termination Criteria for regression tree.
    cat : int
        Cluster possible values of a categorical variable into K <= cat clusters to find a suboptimal split.
    var : int
        Size of the randomly selected subset of features at each tree node.
    nbtrees : int
        Maximum number of trees in the forest.
    acc : float
        Sufficient accuracy (OOB error)
    rand : int
        Seed for random number generation, it ensures reproducibility of results.
    """
    max: int
    min: str
    ra: str
    cat: str
    var: str
    nbtrees: str
    acc: str
    rand : int


class KNNConfig(BaseModel):
    """
    Configuration parameters for the K-Nearest Neighbors (KNN) model of OTB.

    Attributes
    ----------
    k : str
        Number of neighbors to consider.
    rand : int
        Seed for random number generation, it ensures reproducibility of results.
    """
    k: str
    rand : int

class SVMConfig(BaseModel):
    """
    Configuration parameters for the SVM model of scikit-learn.

    Attributes
    ----------
    kernel: str
        kernel type for the model (among 'linear', 'poly', 'rbf', 'sigmoid', or a callable).
    C: float
        Regularization parameter, the strength of the regularization is inversely proportional to C.
    probability : bool
        Whether to enable probability estimates.
    """
    kernel: str
    C: float
    probability: bool

class RFSKConfig(BaseModel):
    """
    Configuration parameters for the Random Forest model of scikit-learn.

    Attributes
    ----------
    n_estimators : int
        The number of trees in the forest, more trees can improve performance but increase computation time.
    max_depth : int
        The maximum depth of each tree, it limits the growth of the trees to prevent overfitting.
    random_state : int
        Controls the randomness of the bootstrapping of samples used when building trees.
    min_samples_split : int
        The minimum number of samples required to split an internal node.
    """
    n_estimators: int
    max_depth: int
    random_state: int
    min_samples_split: int

class ADAConfig(BaseModel):
    """
    Configuration parameters for the AdaBoostClassifier of scikit-learn.

    Attributes
    ----------
    n_estimators: int
        The maximum number of estimators at which boosting is terminated.
    learning_rate : float
        The contribution of each classifier at each boosting iteration.
    random_state : int
        Controls the randomness of the algorithm and ensures reproducibility of results.
    """
    n_estimators: int
    learning_rate: float
    random_state: int

class XTREEConfig(BaseModel):
    """
    Configuration parameters for the ExtraTreesClassifier of scikit-learn.

    Attributes
    ----------
    n_estimators : int
        The number of trees in the forest. More trees can improve performance but increase computation time.
    criterion : str
        The function to measure the quality of a split.
    random_state : int
        Controls the randomness of the estimator and ensures reproducibility when the same value is used.
    """
    n_estimators : int
    criterion : str
    random_state : int

class GRADConfig(BaseModel):
    """
    Configuration parameters for the GradientBoostingClassifier of scikit-learn.

    Attributes
    ----------
    loss: str
        The loss function to be optimized (default = log_loss).
    n_estimators: int
        The number of boosting stages to perform.
    """
    loss: str
    n_estimators: int

class HISTConfig(BaseModel):
    """
    Configuration parameters for the HistGradientBoostingClassifier of scikit-learn.

    Attributes
    ----------
    loss : str
        The loss function to use in the boosting process.
    max_iter: int
        The maximum number of iterations of the boosting process, i.e. the maximum number of trees for binary classification.
    """
    loss : str
    max_iter: int

class MLConfig(BaseModel):
    """
    Configuration for multiple machine learning models.

    Attributes
    ----------
    svm_otb : LibSVMConfig
        Configuration for the LibSVM model of OTB.
    boost_otb : BoostConfig
        Configuration for the Boost model of OTB.
    dt_otb : DTConfig
        Configuration for the Decision Tree model of OTB.
    gbt_otb : GBTConfig
        Configuration for the Gradient Boosted Trees model of OTB.
    ann_otb : ANNConfig
        Configuration for the Artificial Neural Network model of OTB.
    rf_otb : RFConfig
        Configuration for the Random Forest model of OTB.
    knn_otb : KNNConfig
        Configuration for the K-Nearest Neighbors model of OTB.
    svm_scikit : SVMConfig
        Configuration parameters for the SVM model of scikit-learn.
    rf_scikit: RFSKConfig
        Configuration parameters for the Random Forest model of scikit-learn.
    ada_scikit: ADAConfig
        Configuration parameters for the AdaBoostClassifier of scikit-learn.
    xtree_scikit: XTREEConfig
        Configuration parameters for the ExtraTreesClassifier of scikit-learn.
    grad_scikit: GRADConfig
        Configuration parameters for the GradientBoostingClassifier of scikit-learn.
    hist_scikit: HISTConfig
        Configuration parameters for the HistGradientBoostingClassifier of scikit-learn.
    """
    svm_otb: Optional[LibSVMConfig] = None
    boost_otb: Optional[BoostConfig] = None
    dt_otb: Optional[DTConfig] = None
    gbt_otb: Optional[GBTConfig] = None
    ann_otb: Optional[ANNConfig] = None
    rf_otb: Optional[RFConfig] = None
    knn_otb: Optional[KNNConfig] = None
    svm_scikit: Optional[SVMConfig] = None
    rf_scikit: Optional[RFSKConfig] = None
    ada_scikit: Optional[ADAConfig] = None
    xtree_scikit: Optional[XTREEConfig] = None
    grad_scikit: Optional[GRADConfig] = None
    hist_scikit: Optional[HISTConfig] = None