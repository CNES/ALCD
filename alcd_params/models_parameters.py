from typing import Literal, Optional
from pydantic import BaseModel


class LibSVMConfig(BaseModel):
    """
    Configuration parameters for the LibSVM model.

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


class BoostConfig(BaseModel):
    """
    Configuration parameters for the Boost model.

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


class DTConfig(BaseModel):
    """
    Configuration parameters for the Decision Tree (DT) model.

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


class GBTConfig(BaseModel):
    """
    Configuration parameters for the Gradient Boosted Trees (GBT) model.

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


class ANNConfig(BaseModel):
    """
    Configuration parameters for the Artificial Neural Network (ANN) model.

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


class RFConfig(BaseModel):
    """
    Configuration parameters for the Random Forest (RF) model.

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
    """
    max: int
    min: str
    ra: str
    cat: str
    var: str
    nbtrees: str
    acc: str


class KNNConfig(BaseModel):
    """
    Configuration parameters for the K-Nearest Neighbors (KNN) model.

    Attributes
    ----------
    k : str
        Number of neighbors to consider.
    """
    k: str


class MLConfig(BaseModel):
    """
    Configuration for multiple machine learning models.

    Attributes
    ----------
    libsvm : LibSVMConfig
        Configuration for the LibSVM model.
    boost : BoostConfig
        Configuration for the Boost model.
    dt : DTConfig
        Configuration for the Decision Tree model.
    gbt : GBTConfig
        Configuration for the Gradient Boosted Trees model.
    ann : ANNConfig
        Configuration for the Artificial Neural Network model.
    rf : RFConfig
        Configuration for the Random Forest model.
    knn : KNNConfig
        Configuration for the K-Nearest Neighbors model.
    """
    libsvm: Optional[LibSVMConfig] = None
    boost: Optional[BoostConfig] = None
    dt: Optional[DTConfig] = None
    gbt: Optional[GBTConfig] = None
    ann: Optional[ANNConfig] = None
    rf: Optional[RFConfig] = None
    knn: Optional[KNNConfig] = None
