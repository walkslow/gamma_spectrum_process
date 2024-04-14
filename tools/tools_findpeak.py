from scipy import sparse
from scipy.sparse.linalg import spsolve
from scipy.linalg import cholesky
from scipy.optimize import curve_fit
import numpy as np


def arpls(y, lam=1e4, ratio=0.05, itermax=100):
    """
    返回能谱图的基线水平
    :param y: 输入数据，通常是一个光谱或色谱图的数据数组。
    :param lam: 惩罚参数，用于控制加权最小二乘问题中的平滑程度。较大的 lam 值会导致更平滑的基线。
    :param ratio:权重更新的阈值参数。如果权重的变化量小于 ratio 指定的值，则认为迭代已经收敛。
    :param itermax: 执行的最大迭代次数，以防止无限迭代。
    :return: z：基线水平
    """
    N = len(y)
    #  D = sparse.csc_matrix(np.diff(np.eye(N), 2))
    D = sparse.eye(N, format='csc')
    D = D[1:] - D[:-1]  # numpy.diff( ,2) does not work with sparse matrix. This is a workaround.
    D = D[1:] - D[:-1]

    H = lam * D.T * D
    w = np.ones(N)
    for i in range(itermax):
        W = sparse.diags(w, 0, shape=(N, N))
        WH = sparse.csc_matrix(W + H)
        C = sparse.csc_matrix(cholesky(WH.todense()))
        z = spsolve(C, spsolve(C.T, w * y))
        d = y - z
        dn = d[d < 0]
        m = np.mean(dn)
        s = np.std(dn)
        wt = 1. / (1 + np.exp(2 * (d - (2 * s - m)) / s))
        if np.linalg.norm(w - wt) / np.linalg.norm(w) < ratio:
            break
        w = wt
    return z


def gauss(x, H, A, x0, sigma):
    """
    高斯函数
    :param x: 自变量，在这里为能道
    :param H: 基线高度，即没有峰时的背景水平
    :param A: 峰的幅度，即峰的最大值与基线之间的差
    :param x0:峰的中心位置，即峰的对称中心点
    :param sigma:峰的标准差，表示峰的宽度，标准差越大，峰越宽
    :return:根据输入参数计算得到的高斯函数值，即因变量，在这里是计数值
    """
    return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))


def gauss_fit(x, y):
    """
    拟合高斯函数的最佳参数
    :param x:自变量，在这里为能道
    :param y:因变量，在这里为计数值
    :return:最佳拟合参数，即H，A，x0，sigma
    """
    mean = sum(x * y) / sum(y)
    sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
    p0 = [min(y), max(y), mean, sigma]
    try:
        popt, pcov = curve_fit(gauss, x, y, p0=p0)
    except RuntimeError:
        # 如果无法找到最佳参数，返回初始参数，当然，这肯定是不对的！！！
        popt = p0
    return popt


def get_peak(_spec, _range, _address=256):
    """
    获得能谱在某一能道范围内的峰位(单峰位)
    :param _spec: spectrum
    :param _range: range of peak
    :param _address: address of spectrum
    :return: peak
    """
    _add = np.arange(0, _address, 1)
    _window = _spec[_range[0]:_range[1]]
    _baseline = arpls(_window, 1e7, 0.1)
    _g = _window - _baseline
    _popt = gauss_fit(_add[_range[0]:_range[1]], _g)
    return _popt
