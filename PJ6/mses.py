"""AIRFOIL GEOMETRY MANIPULATION - MSES FORMATTING
Logan Halstrom
EAE 127
CREATED: 12 NOV 2015
MODIFIY: 16 NOV 2017


DESCRIPTION: Provides functions for manimulating MSES closed-curve data files.
Split an MSES file into separate upper and lower surfaces.
    Determine splitting location based on reversal of x-coordinate.
Merge separate surface data into single MSES data set.
Interpolate data to match new x vector

IMPROVEMENTS:
    Rework MsesMerge to match format of new MsesSplit
    Rework main to match new functions

"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ReadXfoilGeometry(ifile):
    """Reads MSES two column xfoil output files, including geometry
    and cp distributions.
    ifile --> path to input file (string)
    """
    xgeom, ygeom = np.loadtxt(ifile, skiprows=1, unpack=True)
    return xgeom, ygeom

def FindLE(X):
    """Return index dividing upper and lower surface given MSES format
    geometry.
    MSES files start at rear of airfoil, and x diminishes until the leading
    edge, where it then increases back to the trailing edge.  This code finds
    the transition where x goes from decreasing to increasing.
    X --> MSES x coordinates
    """
    xold = X[0]
    for i, x in enumerate(X[1:]):
        if x >= xold:
            #If current x greater/equal to prev x, x is increasing (lower surf)
            return i #return index of Leading Edge (divides upper/lower surfs)
        else:
            #If current x less than prev x, x still diminishing (upper surf)
            xold = x

def MsesSplit(x, y):
    """Split MSES format into upper and lower surfaces.  Find split from
    x geometry coordinates, split y at this index.  Return y split into
    two sets: upper and lower
    x --> MSES x coordinates
    y --> Any other MSES parameter (e.g. x/c, z/c, Cp, etc)
    """
    #Get index of leading edge on upper surface
    iLE = FindLE(x)
    #Split upper and lower surface, reverse order upper surface
    up = y[iLE::-1]
    lo = y[iLE+1:]
    return up, lo

def MsesInterp(xout, xmses, ymses):
    """Split MSES format data into upper and lower surfaces.  Then
    interpolate data to match given xout vector.
    xout  --> desired x locations
    xmses --> original x MSES data
    ymses --> original x/c, z/c, Cp, etc MSES data
    """
    xup_mses, xlo_mses = MsesSplit(xmses, xmses)
    yup_mses, ylo_mses = MsesSplit(xmses, ymses)
    yup = np.interp(xout, xup_mses, yup_mses)
    ylo = np.interp(xout, xlo_mses, ylo_mses)
    return yup, ylo

def MsesMerge(xlo, xup, ylo, yup):
    """Merge separate upper ant lower surface data into single MSES set.
    xlo, xup --> lower/upper surface x coordinates to merge
    ylo, yup --> lower/upper surface y OR surface Cp values to merge
    """
    #drop LE point of lower surface if coincident with upper surface
    # if xlo[0] == xup[0] and ylo[0] == yup[0]:
    if xlo[0] == xup[0] and ylo[0] == 0 and yup[0] == 0:
        xlo = xlo[1:]
        ylo = ylo[1:]
    n1 = len(xup)     #number of upper surface points
    n = n1 + len(xlo) #number of upper AND lower surface points
    x, y = np.zeros(n), np.zeros(n)
    #reverse direction of upper surface coordinates
    x[:n1], y[:n1] = xup[-1::-1], yup[-1::-1]
    #append lower surface coordinates as they are
    x[n1:], y[n1:] = xlo, ylo
    return x, y


# def dfMsesSplitInterp(xout, df):
#     """Same functionality as MsesSplitInterp, but perform on all columns of
#     an entire pandas dataframe
#     xout  --> desired x locations
#     df    --> dataframe of MSES format data, which includes a column titled 'x'
#     """
#     up = pd.DataFrame({'x' : xout})
#     lo = pd.DataFrame({'x' : xout})
#     for col in list(df.drop('x', axis=1).columns.values):
#         up[col], lo[col] = MsesSplitInterp(xout, df['x'], df[col])
#     return up, lo

# def dfMsesMerge(up, lo):
#     """Same functionality as MsesMerge, but perform on all columns of
#     an entire pandas dataframe
#     """
#     # df = pd.DataFrame({'x' : up.x})
#     df = pd.DataFrame()
#     df['x'], _ = MsesMerge(lo['x'], up['x'], lo['z'], up['z'])
#     for col in list(up.drop('x', axis=1).columns.values):
#         _, df[col] = MsesMerge(lo['x'], up['x'], lo[col], up[col])
#     return df







def main(geom, ):
    """Test code for MSES functions.  Load MSES geometry file, split, and
    re-merge.
    geom --> path to airfoil geometry file
    """

    print('LOAD MSES GEOMETRY')
    x, z = ReadXfoilGeometry(geom)
    print('Raw MSES x:', x)
    print('Raw MSES z:', z)

    print('\nSPLIT MSES GEOMETRY')
    xlo, xup, zlo, zup = MsesSplit(x, z)
    print('Split upper x:', xup)
    print('Split lower x:', xlo)
    print('Split upper z:', zup)
    print('Split lower z:', zlo)

    #dashed lines should perfectly overlap black, no point overlap
    plt.figure()
    plt.title('Compare Original MSES with Split Upper/Lower')
    plt.plot(x, z, color='black', linewidth=5, label='OG MSES')
    plt.plot(xup, zup, color='red', linewidth=2, linestyle='--', label='Upper', marker='.', markersize=15)
    plt.plot(xlo, zlo, color='green', linewidth=2, linestyle='--', label='Lower', marker='.', markersize=8)
    plt.legend(loc='best')
    plt.xlim([-0.05, 1.05])
    plt.show()

    print('\nMERGE SPLIT GEOMETRY')
    xmer, zmer = MsesMerge(xlo, xup, zlo, zup)
    print('Merged MSES x:', xmer)
    print('Merged MSES z:', zmer)

    #Red dots should be centered in black dots
    #and bottom trailing edge should be cut off equally for both
    plt.figure()
    plt.title('Compare Original MSES with Split Upper/Lower')
    plt.plot(x[:-10], z[:-10], color='black', linewidth=5, label='OG MSES', marker='.', markersize=15)
    plt.plot(xmer[:-10], zmer[:-10], color='red', linewidth=2, linestyle='--', label='Merge', marker='.', markersize=8)
    plt.legend(loc='best')
    plt.xlim([-0.05, 1.05])
    plt.show()


    #SPLIT AND INTERPOLATE SURFACE PRESSURE

    x, Cp = np.loadtxt('Data/naca2412_SurfPress_a6.txt', unpack=True, skiprows=1)
    xnew = np.linspace(0, 1, 151)
    x, Cpl, Cpu = MsesSplitInterp(xnew, x, Cp)
    out = np.column_stack((x, Cpl, Cpu))
    np.savetxt('Data/naca2412_SurfPress_a6.csv', out, delimiter=',')

    #SPLIT AND INTERPOLATE SURFACE GEOMETRY
    x, z = np.loadtxt('Data/naca2412_geom.dat', unpack=True, skiprows=1)
    xnew = np.linspace(0, 1, 151)
    x, zlo, zup = MsesSplitInterp(xnew, x, z)
    out = np.column_stack((x, zlo, zup))
    np.savetxt('Data/naca2412_geom_split.dat', out, delimiter=' ')


if __name__ == "__main__":

    foil = 'data/naca2412_geom.dat'
    main(foil)
