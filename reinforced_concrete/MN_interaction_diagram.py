from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from reinforced_concrete.sections import ReinforcedConcreteSection
    from matplotlib.axes import Axes
import numpy as np
import matplotlib.pyplot as plt


def storeToDict(dic, strainRange, N, M, nu, mu):
    dic[strainRange]["N"] = N
    dic[strainRange]["M"] = M
    dic[strainRange]["nu"] = nu
    dic[strainRange]["mu"] = mu


def _strainDistribution_singleArea(section: ReinforcedConcreteSection) -> dict[dict]:
    """
    Return a dictionary with dictionaries for stain ranges (1-6), each with numpy arrays of M, N, mu and nu values
    """
    b = section.b
    As = section.As.area
    As1 = section.As1.area
    d = section.d
    d1 = section.d1
    d2 = section.d2
    h = section.h

    fcd = section.concrete_material.fcd
    fck = section.concrete_material.fck
    Ec = section.concrete_material.Ecm
    ec2 = section.concrete_material.ec2
    ecu = section.concrete_material.ecu2

    fyd = section.As.steel_material.fyd
    fyk = section.As.steel_material.fyk
    Es = section.As.steel_material.Es
    ese = section.As.steel_material.ese
    esu = section.As.steel_material.esu

    fyk1 = section.As1.steel_material.fyk
    ese1 = section.As1.steel_material.ese
    esu1 = section.As1.steel_material.esu

    # Strain Range 2
    def psi_2(xi):
        if xi < 1 / 6:
            return (
                xi / (1 - xi) * esu / (3 * ec2**2) * (3 * ec2 - xi / (1 - xi) * esu)
            )
        else:
            return 1 - (ec2 * (1 - xi)) / (3 * esu * xi)

    def lamb_2(xi):
        # only for n = 2 C<C50/60
        if xi == 0:
            return 0
        elif xi <= 1 / 6:
            return (4 * ec2 - esu * xi / (1 - xi)) / (
                4 * (3 * ec2 - esu * xi / (1 - xi))
            )
        else:
            return (
                (6 * esu**2 + 4 * esu * ec2 + ec2**2) * xi**2
                - 2 * ec2**2 * xi
                + ec2**2
                - 4 * esu * ec2 * xi
            ) / (4 * esu * xi * ((3 * esu + ec2) * xi - ec2))

    def psi_6(xi):
        return (xi**2 - 6 / 7 * xi + 125 / 1029) / (xi - 3 / 7) ** 2

    def lamb_6(xi, t):
        return (
            3
            / 14
            * ((2401 * xi**2 - 2058 * xi + 185) / (1029 * xi**2 - 882 * xi + 125))
        )

    # return (1/2 + 1/3 * ec2/ecu * ((1-t/h)/(xi-t/h))**2 * (-1 + 1/4*ec2/ecu))/(1/(3*ecu) * (3*ecu - ec2*((1-t/h)/(xi-t/h))**2))

    xi23 = ecu / (ecu + esu)
    xi34 = ecu / (ecu + ese)
    xi1a1b = (esu * d2 - ese1 * d) / (d * (esu - ese1))
    dic = {}

    # ---------------------------------------------------------------------
    # ------------------------------ CAMPO 1 ------------------------------
    # ---------------------------------------------------------------------

    strainRange = "1"
    dic[strainRange] = {}
    xi = np.linspace(-50 / d, 0, 20)
    x = xi * d
    es1 = (esu * (d2 - x)) / (
        d - x
    )  # TODO tanto vale mettere la formula con xi (ovunque)

    fyd1 = []
    for i in range(len(es1)):
        if abs(es1[i]) > ese1:
            fyd1.append(fyk1 / 1.15)
        else:
            fyd1.append(Es * es1[i])
    fyd1 = np.array(fyd1)

    N = -fyd1 * As1 - fyd * As
    M = -fyd1 * As1 * (h / 2 - d2) + fyd * As * (h / 2 - d1)
    nu = N / (b * d * fcd)
    mu = M / (b * d**2 * fcd)
    storeToDict(dic, strainRange, N, M, nu, mu)
    # ---------------------------------------------------------------------
    # ------------------------------ CAMPO 2 ------------------------------
    # ---------------------------------------------------------------------

    strainRange = "2"
    dic[strainRange] = {}

    xi = np.linspace(0, xi23, 130)
    x = xi * d
    es1 = -(esu * (x - d2)) / (
        d - x
    )  # TODO tanto vale mettere la formula con xi (ovunque)

    fyd1 = []
    for i in range(len(es1)):
        if abs(es1[i]) > ese1 and es1[i] > 0:
            fyd1.append(fyk1 / 1.15)
        elif abs(es1[i]) > ese1 and es1[i] < 0:
            fyd1.append(-fyk1 / 1.15)
        else:
            fyd1.append(Es * es1[i])
    fyd1 = np.array(fyd1)

    psi = np.array([psi_2(xi_i) for xi_i in xi])
    lamb = np.array([lamb_2(xi_i) for xi_i in xi])

    N = b * psi * x * fcd - fyd1 * As1 - fyd * As
    M = (
        b * psi * x * fcd * (h / 2 - lamb * x)
        - fyd1 * As1 * (h / 2 - d2)
        + fyd * As * (h / 2 - d1)
    )
    nu = N / (b * d * fcd)
    mu = M / (b * d**2 * fcd)

    storeToDict(dic, strainRange, N, M, nu, mu)

    # ---------------------------------------------------------------------
    # ------------------------------ CAMPO 3 ------------------------------
    # ---------------------------------------------------------------------

    strainRange = "3"
    dic[strainRange] = {}

    fyd = fyk / 1.15

    xi = np.linspace(xi23, xi34, 100)
    x = xi * d

    es1 = -ecu * (x - d2) / x

    # fyd1 = -fyk1/1.15
    fyd1 = []
    for i in range(len(es1)):
        if abs(es1[i]) > ese1 and es1[i] > 0:
            fyd1.append(fyk1 / 1.15)
        elif abs(es1[i]) > ese1 and es1[i] < 0:
            fyd1.append(-fyk1 / 1.15)
        else:
            fyd1.append(Es * es1[i])
    fyd1 = np.array(fyd1)

    psi = 17 / 21  # 0.8095238095238095
    lamb = 99 / 238  # 0.4159663865546219

    # solo campo 3B. Da capire il 3A perché non lo considera!

    N = b * psi * x * fcd - fyd1 * As1 - fyd * As
    M = (
        b * psi * x * fcd * (h / 2 - lamb * x)
        - fyd1 * As1 * (h / 2 - d2)
        + fyd * As * (h / 2 - d1)
    )
    nu = N / (b * d * fcd)
    mu = M / (b * d**2 * fcd)

    storeToDict(dic, strainRange, N, M, nu, mu)

    # ---------------------------------------------------------------------
    # ------------------------------ CAMPO 4 ------------------------------
    # ---------------------------------------------------------------------

    strainRange = "4"
    dic[strainRange] = {}

    xi = np.linspace(xi34, 1, 100)
    x = xi * d

    es1 = -ecu * (x - d2) / x
    es = ecu * (d - x) / x

    fyd1 = -fyk1 / 1.15
    fyd = Es * es

    psi = 17 / 21  # 0.8095238095238095
    lamb = 99 / 238  # 0.4159663865546219

    N = b * psi * x * fcd - fyd1 * As1 - fyd * As
    M = (
        b * psi * x * fcd * (h / 2 - lamb * x)
        - fyd1 * As1 * (h / 2 - d2)
        + fyd * As * (h / 2 - d1)
    )
    nu = N / (b * d * fcd)
    mu = M / (b * d**2 * fcd)

    storeToDict(dic, strainRange, N, M, nu, mu)

    # ---------------------------------------------------------------------
    # ------------------------------ CAMPO 5 ------------------------------
    # ---------------------------------------------------------------------

    strainRange = "5"
    dic[strainRange] = {}

    xi = np.linspace(1, 1 + d1 / d, 50)
    x = xi * d

    es1 = -ecu * (x - d2) / x
    es = -ecu * (d - x) / x

    fyd1 = -fyk1 / 1.15
    fyd = -Es * es
    psi = 17 / 21  # 0.8095238095238095
    lamb = 99 / 238  # 0.4159663865546219

    N = b * psi * x * fcd - fyd1 * As1 - fyd * As
    M = (
        b * psi * x * fcd * (h / 2 - lamb * x)
        - fyd1 * As1 * (h / 2 - d2)
        + fyd * As * (h / 2 - d1)
    )
    nu = N / (b * d * fcd)
    mu = M / (b * d**2 * fcd)

    storeToDict(dic, strainRange, N, M, nu, mu)

    # ---------------------------------------------------------------------
    # ------------------------------ CAMPO 6 ------------------------------
    # ---------------------------------------------------------------------

    strainRange = "6"
    dic[strainRange] = {}

    xi = np.linspace(1 + d1 / d, 50, 200)
    x = xi * d

    t = (ecu - ec2) * (d + d1) / ecu  # C<C50/60: 3/7 * h

    es1 = -ec2 * (x - d2) / (x - t)
    es = -ec2 * (x - d) / (x - t)

    fyd1 = -fyk1 / 1.15

    # x6a6b = (ec2 * d + ese * t)/(ec2 + ese)

    fyd = []
    for i in range(len(x)):
        if abs(es[i]) < ese:
            fyd.append(Es * es[i])
        else:
            fyd.append(-fyk / 1.15)
    fyd = np.array(fyd)

    psi = np.array([psi_6(xi_i) for xi_i in xi])
    lamb = np.array([lamb_6(xi_i, t) for xi_i in xi])
    psi[0] = 17 / 21  # 0.8095238095238095
    lamb[0] = 99 / 238  # 0.4159663865546219

    N = b * psi * h * fcd - fyd1 * As1 - fyd * As
    M = (
        b * psi * h * fcd * (h / 2 - lamb * h)
        - fyd1 * As1 * (h / 2 - d2)
        + fyd * As * (h / 2 - d1)
    )
    nu = N / (b * d * fcd)
    mu = M / (b * d**2 * fcd)

    storeToDict(dic, strainRange, N, M, nu, mu)

    return dic


class MN_InteractionDiagram:
    def __init__(self, list_of_sections: list[ReinforcedConcreteSection]):
        self.list_of_sections = list_of_sections

        self._COLORS = [
            list(plt.rcParams["axes.prop_cycle"])[col]["color"]
            for col in range(len(list(plt.rcParams["axes.prop_cycle"])))
        ]  # colors from the matplotlib style

    def _plot_multiple(
        self, ax: Axes, section: ReinforcedConcreteSection, MN: bool = True
    ):
        dict_up = _strainDistribution_singleArea(section)
        dict_down = _strainDistribution_singleArea(section.create_inverted_section())
        if MN:
            x = "N"
            coef_x = 1.0e3  # N -> kN
            y = "M"
            coef_y = 1.0e6  # Nmm -> kNm
        else:
            x = "nu"
            coef_x = 1.0
            y = "mu"
            coef_y = 1.0

        for i in range(1, 7):
            ax.plot(
                dict_up[f"{i}"][x] / coef_x,
                dict_up[f"{i}"][y] / coef_y,
                dict_down[f"{i}"][x] / coef_x,
                -dict_down[f"{i}"][y] / coef_y,
                color=self._COLORS[i - 1],
            )

        # plt.savefig(f"{y}_{x}_diagram_multiple.pdf")
        x_max = dict_up["3"][x][-1] / coef_x
        y_max = dict_up["3"][y][-1] / coef_y
        return ax, x_max, y_max

    def plot(
        self,
        ax: Axes | None = None,
        MN: bool = True,
        points: list[tuple[float, float, str]] | None = None,
    ):
        "points: None or a list of tuples like: (M[kNm], N[kN], str) or (mu[-]], nu[-], str)"
        if ax is None:
            _, ax = plt.subplots(1, 1, figsize=(12, 7))
        if MN:
            ax.set_xlabel(r"$N \, \text{[kN]}$")
            ax.set_ylabel(r"$M \, \text{[kNm]}$")
            ax.set_title(f"Diagramma M - N", fontsize=14)
        else:
            ax.set_xlabel(r"$\nu \, [-]$ ")
            ax.set_ylabel(r"$\mu \, [-]$")
            ax.set_title(f"Diagramma M - N adimensionalizzato", fontsize=14)

        ax.grid("True", which="both", linestyle="dashed")
        section_labels = []
        for i, section in enumerate(self.list_of_sections):
            ax, x_max, y_max = self._plot_multiple(ax, section, MN)
            number = ""
            if len(self.list_of_sections) > 1:
                number = f"{i+1}) "
                ax.annotate(
                    text=f"{i+1}",
                    xy=(x_max, y_max),
                    xycoords="data",
                    xytext=(5, 5),
                    textcoords="offset points",
                    bbox=dict(boxstyle="circle", fc="w", ec="0.5", alpha=0.9),
                )
            label = f"{number}{section.b} x {section.h}, {section.As.__str__()} + {section.As1.__str__()}"
            section_labels.append(label)
            #
        sections_legend = ax.legend(
            labels=section_labels,
            loc="upper left",
            frameon="True",
            # to remove the lines in the legend:
            handlelength=0,
            handletextpad=0,
        )
        ax.add_artist(sections_legend)

        if points is not None:
            pp = []
            for point in points:
                (p,) = ax.plot(point[0], point[1], "X", label=point[2])
                pp.append(p)
            points_legend = ax.legend(handles=pp, loc="upper right", frameon="True")
            ax.add_artist(points_legend)
        return ax
