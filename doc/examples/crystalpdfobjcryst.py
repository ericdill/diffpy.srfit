#!/usr/bin/env python
########################################################################
#
# diffpy.srfit      by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
########################################################################
"""Example of using ProfileGenerators in FitContributions.

This is an example of building a ProfileGenerator and using it in a
FitContribution in order to fit theoretical intensity data.

The IntensityGenerator class is an example of a ProfileGenerator that can be
used by a FitContribution to help generate a signal.

The makeRecipe function shows how to build a FitRecipe that uses the
IntensityGenerator.

"""

import os

import numpy

from pyobjcryst.crystal import CreateCrystalFromCIF

from diffpy.srfit.pdf import PDFGenerator, PDFParser
from diffpy.srfit.fitbase import Profile
from diffpy.srfit.fitbase import FitContribution, FitRecipe
from diffpy.srfit.fitbase import FitResults

from gaussianrecipe import scipyOptimize, parkOptimize
from crystalpdf import plotResults

####### Example Code

def makeRecipe(ciffile, datname):
    """Create a recipe that uses the IntensityGenerator.

    This will create a FitContribution that uses the IntensityGenerator,
    associate this with a Profile, and use this to define a FitRecipe.

    """

    ## The Profile
    profile = Profile()

    # Load data and add it to the profile
    parser = PDFParser()
    parser.parseFile(datname)
    profile.loadParsedData(parser)
    profile.setCalculationRange(xmax = 20)

    ## The ProfileGenerator
    generator = PDFGenerator("G")
    stru = CreateCrystalFromCIF(file(ciffile))
    generator.setPhase(stru)
    generator.setQmax(40.0)
    
    ## The FitContribution
    contribution = FitContribution("nickel")
    contribution.addProfileGenerator(generator)
    contribution.setProfile(profile, xname = "r")

    # Make the FitRecipe and add the FitContribution.
    recipe = FitRecipe()
    recipe.addContribution(contribution)

    phase = generator.phase

    recipe.addVar(generator.scale, 1)
    recipe.addVar(generator.qdamp, 0.01)
    recipe.addVar(generator.delta2, 5)
    lattice = phase.getLattice()
    recipe.addVar(lattice.a)
    # We don't need to constrain 'b' and 'c', this is already done for us,
    # consistent with the space group of the crystal.

    Biso = recipe.newVar("Biso", 0.5)
    for scatterer in phase.getScatterers():
        recipe.constrain(scatterer.Biso, Biso)

    # Give the recipe away so it can be used!
    return recipe

if __name__ == "__main__":

    # Make the data and the recipe
    ciffile = "data/ni.cif"
    data = "data/ni-q27r100-neutron.gr"

    # Make the recipe
    recipe = makeRecipe(ciffile, data)

    # Optimize
    scipyOptimize(recipe)
    #parkOptimize(recipe)

    # Generate and print the FitResults
    res = FitResults(recipe)
    res.printResults()

    # Plot!
    plotResults(recipe)

# End of file
