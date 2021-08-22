#!/usr/bin/env python

# Matplotlib
# https://matplotlib.org/2.2.2/index.html
# Matplotlib Toolkit mplot3d
# https://matplotlib.org/2.2.2/mpl_toolkits/index.html
# example:
# https://jakevdp.github.io/PythonDataScienceHandbook/04.12-three-dimensional-plotting.html


from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import statistics as stats
from enum import Enum, IntEnum
from pint import UnitRegistry
u = UnitRegistry()
symOmega = '\u03A9'
symMu = '\u03BC'
symDot = '\u00B7'

def plus_or_minus( value, tolerance ):
  return value, value+tolerance, value-tolerance

class Value:
  def __init__( self, units, val1, val2=None, val3=None ):
    # simplest condition, only val1 is given
    self.value = val1 * units
    self.valmin = val1 * units
    self.valmax = val1 * units
    self.units = units
    if val2 is not None: # val2 is given
      if val3 is not None: # val2 and val3 are given: non,min,max
        self.valmin = val2 * units
        self.valmax = val3 * units
      else: # only val2 is given: min,max
        self.valmin = val1 * units
        self.valmax = val2 * units
        self.value = 0.5 * (val1 + val2) * units
  def __str__(self):
    return '{self.value.magnitude}, from {self.valmin.magnitude} to {self.valmax.magnitude} {self.value.units}'.format(self=self)
  def __repr__(self):
    return '{self.value}'.format(self=self)

class Category(IntEnum):
  metal = 1
  flexo = 2
  inkjet = 3
  screen = 4
  aerosol = 5
  carbon = 6

Catname = { Category.metal: 'metal', Category.flexo: 'flexo', 
            Category.inkjet: 'inkjet', Category.screen: 'screen',
            Category.aerosol: 'aerosol', Category.carbon: 'carbon' }

class PCB_weight:
  def __init__(self, weight, microns, mils):
    self.weight = weight
    self.microns = microns
    self.mils = mils

pcb_weights = [
    PCB_weight( 0.5,  17.4, 0.7 ),
    PCB_weight( 1.0,  34.8, 1.4 ),
    PCB_weight( 2.0,  69.6, 2.8 ),
    PCB_weight( 4.0, 139.2, 5.6 ),
  ]

class Trace:
  def __init__(self, length, width, thickness):
    self.length = length
    self.width = width
    self.thickness = thickness
    self.area = self.length * self.width
    self.squares = self.length / self.width

class Material:
  index={}
  @staticmethod
  def indexer(cat):
    catfactor = 20
    catstep = 1
    if cat in Material.index:
      Material.index[cat] += catstep
    else:
      Material.index[cat] = catfactor*cat 
    return Material.index[cat]

  def __init__( self, cat, name, r_bulk, thickness=None, r_sheet=None  ):
     self.cat = cat 
     self.name = name
     self.r_bulk = r_bulk
     self.r_sheet = r_sheet
     self.thickness = thickness
     self.index = Material.indexer(cat)

# These are temporary, will be deleted down below
# so the data table doesn't have crazy long lines
V = Value
C = Category
M = Material
PM = plus_or_minus
# These we'll keep around becuase they're useful
BR = 1 * u.uohm * u.cm
SR = 1 * u.mohm
TH = 1 * u.micron

matls = [
  M( C.metal,   'silver',      V( BR, *PM(  1.60, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'copper',      V( BR, *PM(  1.70, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'gold',        V( BR, *PM(  2.40, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'aluminium',   V( BR, *PM(  2.80, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'zinc',        V( BR, *PM(  5.50, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'nickel',      V( BR, *PM(  7.00, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'brass',       V( BR, *PM(  7.50, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'platinum',    V( BR, *PM(  9.80, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'iron',        V( BR, *PM( 10.00, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'tin',         V( BR, *PM( 11.00, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),
  M( C.metal,   'lead',        V( BR, *PM( 19.00, 0.1 ) ),               V( TH,   34.8,  17.4,   69.6  ) ),

  M( C.flexo,   'pfi-500',     V( BR,  8.00,  7.00,  9.00 ),  V( TH,  0.510,  0.120,  0.900 ) ),
  M( C.flexo,   'pfi-600',     V( BR,  6.00,  5.00,  7.00 ),  V( TH,  0.770,  0.140,  1.400 ) ),
  M( C.flexo,   'pfi-722',     V( BR,  6.00,  5.00,  7.00 ),  V( TH,  0.770,  0.140,  1.400 ) ),
  M( C.flexo,   'pfi-rsa6004', V( BR, 11.00, 10.00, 12.00 ),  V( TH,  0.303,  0.125,  0.480 ) ),
  M( C.flexo,   'pfi-rsa6012', V( BR,  9.00,  8.00, 10.00 ),  V( TH,  0.315,  0.130,  0.500 ) ),

  M( C.inkjet,  'ci-004',      V( BR, 12.00, 12.00, 12.00 ),  V( TH,  1.000,  0.200,  2.000 ) ),
  M( C.inkjet,  'ci-005',      V( BR,  9.00,  9.00,  9.00 ),  V( TH,  1.000,  0.200,  2.000 ) ),
  M( C.inkjet,  'ici-002hv',   V( BR,  9.15,  7.50, 10.80 ),  V( TH,  1.000,  0.200,  2.000 ) ),
  M( C.inkjet,  'js-a101a',    V( BR, 19.40,  7.80, 31.00 ),  V( TH,  1.000,  0.200,  2.000 ) ),
  M( C.inkjet,  'js-a102a',    V( BR, 19.40,  7.80, 31.00 ),  V( TH,  1.000,  0.200,  2.000 ) ),
  M( C.inkjet,  'js-a191',     V( BR, 19.40,  7.80, 31.00 ),  V( TH,  1.000,  0.200,  2.000 ) ),
  M( C.inkjet,  'js-b25hv',    V( BR,  2.80,  2.80,  2.80 ),  V( TH,  1.000,  0.200,  2.000 ) ),
#  M( C.inkjet,  'js-b25p',     V( BR,  0.46,  0.36,  0.56 ),  V( TH,  1.000,  0.200,  2.000 ) ),
#  M( C.inkjet,  'js-b40g',     V( BR, 17.50,  0.30,  0.40 ),  V( TH,  1.000,  0.200,  2.000 ) ),

  M( C.screen,  'cp-007',      V( BR, 17.50, 17.50, 17.50 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'cp-008',      V( BR, 25.00, 25.00, 25.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'cp-009',      V( BR, 25.00, 25.00, 25.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'hps-021lv',   V( BR, 10.00, 10.00, 10.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
 #M( C.screen,  'hps-030lv',   V( BR, 40.00,  2.00, 80.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'hps-fg32',    V( BR, 17.50, 11.00, 24.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'hps-fg57b',   V( BR, 19.00, 22.00, 27.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'ici-021',     V( BR, 50.00, 50.00, 50.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'psi-211',     V( BR,  9.00,  9.00,  9.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),
  M( C.screen,  'psi-219',     V( BR, 11.00, 11.00, 11.00 ),  V( TH,  15.0,    5.0,   30.0  ) ),

  M( C.aerosol, 'ci-006',      V( BR,  5.10,  3.40,  6.80 ),  V( TH,  2.00,   1.00,   5.00 ) ),
#  M( C.aerosol, 'hps-108ae1',  V( BR,257.00, 14.00,500.00 ),  V( TH,  2.00,   1.00,   5.00 ) ),
#  M( C.aerosol, 'js-a221ae',   V( BR,214.00,  9.10,420.00 ),  V( TH,  2.00,   1.00,   5.00 ) ),
  M( C.aerosol, 'pspi-1000',   V( BR,  8.50,  8.50,  8.50 ),  V( TH,  2.00,   1.00,   5.00 ) ),

#  M( C.flexo,   'pfi-500',     V( BR,  8.00,  7.00,  9.00 ),  V( TH,  0.510,  0.116666666,  0.900 ),  V( SR, 350, 100, 600 ) ),
#  M( C.flexo,   'pfi-600',     V( BR,  6.00,  5.00,  7.00 ),  V( TH,  0.770,  0.140,  1.400 ),  V( SR, 200,  50, 350 ) ),
#  M( C.flexo,   'pfi-722',     V( BR,  6.00,  5.00,  7.00 ),  V( TH,  0.770,  0.140,  1.400 ),  V( SR, 200,  50, 350 ) ),
#  M( C.flexo,   'pfi-rsa6004', V( BR, 11.00, 10.00, 12.00 ),  V( TH,  0.303,  0.120,  0.480 ),  V( SR, 525, 250, 800 ) ),
#  M( C.flexo,   'pfi-rsa6012', V( BR,  9.00,  8.00, 10.00 ),  V( TH,  0.315,  0.130,  0.500 ),  V( SR, 400, 200, 600 ) ),
#
  M( C.carbon,  'jr-700lv',     V( BR, 1.200e6, 1.100e6, 1.300e6 ),  V( TH,  1.000,  0.200,  2.000 ) ), # inkjet
  M( C.carbon,  'jr-700hv',     V( BR, 0.550e6, 0.520e6, 0.850e6 ),  V( TH,  1.000,  0.200,  2.000 ) ), # inkjet
  M( C.carbon,  'hpr-059',      V( BR, 0.762e6, 0.698e6, 0.889e6 ),  V( TH, 20.000,  5.000, 50.000 ) ), # screen

]

del V
del C
del M


byname = { x.name:x for x in matls }
#bymetals = [ x for x in matls if x.cat is Category.metal ]
bymetals = [ byname['silver'], byname['copper'], byname['gold'] ]
bycopper = [ byname['copper'] ]
byflexo = [ x for x in matls if x.cat is Category.flexo ]
byinkjet = [ x for x in matls if x.cat is Category.inkjet ]
byscreen = [ x for x in matls if x.cat is Category.screen ]
byaerosol = [ x for x in matls if x.cat is Category.aerosol ]
bycarbon = [ x for x in matls if x.cat is Category.carbon ]


# This only used to back out thickness from certain data sheets
def print_thickness( matl ):
  for br in [ matl.r_bulk.valmin, matl.r_bulk.valmax ]:
    for sr in [ matl.r_sheet.valmin,  matl.r_sheet.valmax ]:
      th = (br / sr).to(u.micron)
      print( br, sr, th )

def print_sheet_resistance( matl ):
  for br in [ matl.r_bulk.valmin, matl.r_bulk.valmax ]:
    for th in [ matl.thickness.valmin,  matl.thickness.valmax ]:
      sr = (br / th)
      print( br, th, sr )


def calc_sr( br, th ):
  sr_units = ( (br*BR) / (th*TH) ).to(SR.units)
  sr = sr_units.magnitude
  return sr

def calc_sr_units( br, th ):
  sr_units = ( (br*BR) / (th*TH) ).to(SR.units)
  return sr_units

def divide_interval( value, num ):
    # make min/max values array
    valmin = value.valmin.magnitude
    valmax = value.valmax.magnitude
    if valmin == valmax:
      interval = np.full( num, valmin )
    else:
      interval = np.linspace( valmin, valmax, num )
    return interval

def print_sheet_resistance(m):
    # make min/max values for Bulk resistivity and Thickness
    brlist = divide_interval( m.r_bulk, 10 )
    thlist = divide_interval( m.r_bulk, 10 )
    for br in brlist:
      for th in thlist:
        sr_units = ( (br*BR) / (th*TH) ).to(SR.units)
        sr = sr_units.magnitude
        print( br, th, sr )


class Plot3D:
  def __init__(self, scatter=False, wireframe=True, trisurface=False):
    self.scatter_plot = scatter
    self.wireframe_plot = wireframe
    self.trisurface_plot = trisurface
    self.fig = plt.figure()
    self.ax = plt.axes(projection='3d')
    self.ax.set_xlabel('bulk resistivity')
    self.ax.set_ylabel('thickness')
    self.ax.set_zlabel('sheet resistance')
    #self.ax.set_xlim(0, 100)
    #self.ax.set_ylim(0, 50)

  def sheet_resistance( self, mlist, plotcolor ):
    if self.scatter_plot:
      for m in mlist:
        if m is None: continue
        # make min/max values for Bulk resistivity and Thickness
        brlist = divide_interval( m.r_bulk, 10 )
        thlist = divide_interval( m.thickness, 10 )

        xdata = []
        ydata = []
        zdata = []
        # outer loop over N values of bulk resistivity
        for br in brlist:
          # inner loop over values of thickness
          for th in thlist:
            sr_units = ( (br*BR) / (th*TH) ).to(SR.units)
            sr = sr_units.magnitude
            xdata.append( br )
            ydata.append( th )
            zdata.append( sr )
        x = np.array(xdata)
        y = np.array(ydata)
        z = np.log10( np.array(zdata) )
        #self.ax.scatter3D(x, y, z, c=z, cmap='Greens');
        self.ax.scatter3D(x, y, z, color=plotcolor)
        #self.ax.set_zscale('log')
      
    ### wire frame plot example
    if self.wireframe_plot:
      for m in mlist:
        if m is None: continue
        # make min/max values for Bulk resistivity and Thickness
        brlist = divide_interval( m.r_bulk, 10 )
        thlist = divide_interval( m.thickness, 10 )
        X,Y = np.meshgrid(brlist,thlist)
        Z = np.log10( calc_sr(X,Y) )
        #ax.contour3D(X, Y, Z, 50, cmap='binary' )
        #ax.plot_wireframe(X, Y, Z, color='black' )
        #ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
        self.ax.plot_surface(X, Y, Z, color=plotcolor, edgecolor='none')

    ### surface frame plot example
    if self.trisurface_plot:

      ##  brlist = np.array([])
      ##  thlist = np.array([])
      ##  for m in mlist:
      ##    if m is None: continue
      ##    # make min/max values for Bulk resistivity and Thickness
      ##    brlist = np.append( brlist, divide_interval( m.r_bulk, 10 ) )
      ##    thlist = np.append( thlist, divide_interval( m.thickness, 10 ) )

      ##  X,Y = np.meshgrid(brlist,thlist)
      ##  Z = np.log10( calc_sr(X,Y) )

      ##  print( np.amin(X), np.amax(X) )
      ##  print( np.amin(Y), np.amax(Y) )
      ##  print( np.amin(Z), np.amax(Z) )

      for m in mlist:
        xdata = []
        ydata = []
        zdata = []
        for br in [ m.r_bulk.valmin, m.r_bulk.valmax ]:
          for th in [ m.thickness.valmin, m.thickness.valmax ]:
            xdata.append( br.magnitude )
            ydata.append( th.magnitude )
            zdata.append( calc_sr( br.magnitude, th.magnitude))


      cube = np.array( [ 
        [ min(xdata), min(ydata), min(zdata) ],
        [ min(xdata), max(ydata), min(zdata) ],
        [ max(xdata), max(ydata), min(zdata) ],
        [ max(xdata), min(ydata), min(zdata) ],
        [ min(xdata), min(ydata), max(zdata) ],
        [ min(xdata), max(ydata), max(zdata) ],
        [ max(xdata), max(ydata), max(zdata) ],
        [ max(xdata), min(ydata), max(zdata) ] ] )

      self.ax.plot_surface(cube, color=plotcolor, edgecolor='none')


      print( min(xdata), max(xdata) )
      print( min(ydata), max(ydata) )
      print( min(zdata), max(zdata) )


      ###  #ax.contour3D(X, Y, Z, 50, cmap='binary' )
      ###  #ax.plot_wireframe(X, Y, Z, color='black' )
      ###  #self.ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')
      ###  self.ax.plot_surface(X, Y, Z, color=plotcolor, edgecolor='none')
      ###  #self.ax.plot_trisurf(X, Y, Z, color=plotcolor, edgecolor='none')

  def display( self ):
    plt.show()


class Plot2D:
  def __init__(self, scatter=True):
    self.scatter_plot = scatter
    self.fig,self.ax = plt.subplots()
    self.begin=True

  def bulk_resistivity( self, mlist, plotcolor ):
    if self.begin:
      br_units = symMu + symOmega + symDot + 'cm'
      self.ax.set_title('Bulk Resistivity of Various Materials')
      self.ax.set_xlabel('Material')
      self.ax.grid(True, which='both', axis='y')
      self.ax.set_xlim(10, 115)
      self.ax.get_xaxis().set_ticks( [18,38,58,78,98] )
      self.ax.get_xaxis().set_ticklabels( 
          [ Catname[Category.metal], 
            Catname[Category.flexo], 
            Catname[Category.inkjet],
            Catname[Category.screen],
            Catname[Category.aerosol] ] 
          )
      self.ax.set_ylabel('Bulk resistivity in ' + br_units)
      self.begin = False

    if mlist is None: return
    index = [ m.index for m in mlist ]
    xdata = []
    ydata = []
    for m in mlist:
      for br in [ m.r_bulk.valmin, m.r_bulk.valmax ]:
        xdata.append( m.index )
        ydata.append( br.magnitude )

    x = np.array(xdata)
    y = np.array(ydata)
    self.ax.scatter(x,y, color=plotcolor, s=100)
    #self.ax.legend( [ mlist[0].cat ] )
      
  def sheet_resistance( self, mlist, plotcolor, units='mOhms/Sq' ):
    if self.begin:
      if units =='mOhms/Sq':
        sr_units = 'm' + symOmega + '/sq'
      elif units =='Ohms/Sq':
        sr_units = symOmega + '/sq'
      else:
        return
      self.ax.set_title('Sheet Resistances at Typical Thicknesses')
      self.ax.set_xlabel('Material')
      self.ax.grid(True, which='major', axis='y')
      self.ax.set_xlim(10, 130)
      self.ax.get_xaxis().set_ticks( [18,38,58,78,98, 118] )
      self.ax.get_xaxis().set_ticklabels( 
          [ 'copper', 
            Catname[Category.flexo], 
            Catname[Category.inkjet],
            Catname[Category.screen],
            Catname[Category.aerosol],
            Catname[Category.carbon] ] 
          )
      self.ax.set_ylabel('Sheet Resistance in ' + sr_units)
      self.ax.grid(True, which='both', axis='y')
      self.begin = False

    if mlist is None: return
    xdata = []
    ydata = []
    index = [ m.index for m in mlist ]
    for m in mlist:
      for br in [ m.r_bulk.valmin, m.r_bulk.valmax ]:
        if m.cat == Category.metal:
          thlist = [ w.microns for w in pcb_weights ]
        else:
          thlist = divide_interval( m.thickness, 10 )
        for th in thlist:
          sr = calc_sr( br.magnitude, th)
          if units =='mOhms/Sq':
            pass # default SR is already mOhms/Sq
          elif units =='Ohms/Sq':
            sr = sr / 1000.0
          else: 
            exit(0)
          xdata.append( m.index )
          ydata.append( sr )
          if m.cat == Category.metal:
            print(f'{br.magnitude:.2f}\t{th:.2f}\t{sr:.2f}' )

    x = np.array(xdata)
    y = np.log10( np.array(ydata) )
    #breakpoint()
    self.ax.scatter(x,y, color=plotcolor, s=64)
    #self.ax.plot(x,y, marker='o', linewidth=0, color=plotcolor)
    #self.ax.set_yscale('log')
    if units =='mOhms/Sq':
      self.ax.get_yaxis().set_ticks( [-1,0,1,2,3,4,5,6,7,8] )
      self.ax.set_yticklabels([0.1, 1, 10, 100, '1K', '10K', '100K', '1M', '10M', '100M' ])
    elif units =='Ohms/Sq':
      self.ax.get_yaxis().set_ticks( [-3,-2,-1,0,1,2,3,4,5] )
      self.ax.set_yticklabels([0.001, 0.01, 0.1, 1, 10, 100, '1K', '10K', '100K' ])
    else: 
      exit(0)

  def thickness( self, mlist, plotcolor ):
    if self.begin:
      th_units = symMu + 'm'
      self.ax.set_title('Typical Thicknesses by Material Type')
      self.ax.set_xlabel('Material')
      self.ax.grid(True, which='major', axis='y')
      self.ax.set_xlim(10, 115)
      self.ax.get_xaxis().set_ticks( [18,38,58,78,98] )
      self.ax.get_xaxis().set_ticklabels( 
          [ 'copper', 
            Catname[Category.flexo], 
            Catname[Category.inkjet],
            Catname[Category.screen],
            Catname[Category.aerosol] ] 
          )
      self.ax.set_ylabel('Sheet Thickness in ' + th_units )
      self.begin = False

    if mlist is None: return
    index = [ m.index for m in mlist ]
    xdata = []
    ydata = []
    for m in mlist:
      if m.cat == Category.metal:
        thlist = [ w.microns for w in pcb_weights ]
      else:
        thlist = divide_interval( m.thickness, 25 )
      for th in thlist:
        xdata.append( m.index )
        ydata.append( th )

    x = np.array(xdata)
    #y = np.array(ydata)
    y = np.log10( np.array(ydata) )
    self.ax.scatter(x,y, color=plotcolor, s=64)
    #self.ax.set_yscale('log')
    self.ax.get_yaxis().set_ticks( [-2,-1,0,1, 2, 2.3 ] )
    self.ax.set_yticklabels([0.01, 0.1, 1, 10, 100, 200 ])
      
  def trace_resistance( self, trace, mlist, plotcolor, title='Resistances of Trace' ):
    if self.begin:
      tr_units = symOmega 
      self.ax.set_title(title)
      self.ax.set_xlabel('Material')
      self.ax.grid(True, which='major', axis='y')
      self.ax.set_xlim(10, 130)
      self.ax.get_xaxis().set_ticks( [18,38,58,78,98,118] )
      self.ax.get_xaxis().set_ticklabels( 
          [ 'copper', 
            Catname[Category.flexo], 
            Catname[Category.inkjet],
            Catname[Category.screen],
            Catname[Category.aerosol],
            Catname[Category.carbon] ] 
          )
      self.ax.set_ylabel('Trace Resistance in ' + tr_units)
      self.ax.grid(True, which='both', axis='y')
      self.begin = False

    if mlist is None: return
    xdata = []
    ydata = []
    index = [ m.index for m in mlist ]
    ohms = [] 
    for m in mlist:
      for br in [ m.r_bulk.valmin, m.r_bulk.valmax ]:
        if m.cat == Category.metal:
          thlist = [ w.microns for w in pcb_weights ]
        else:
          thlist = divide_interval( m.thickness, 10 )
        for th in thlist:
          sr = calc_sr_units( br.magnitude, th)
          tr = (sr * trace.squares).to(u.ohms);
          xdata.append( m.index )
          ydata.append( tr.magnitude )
          ohms.append( tr.magnitude )
          if m.cat == Category.metal:
            print( m.name, th, end='\t' )
            print( f'{tr.magnitude:.3f}' )

    if m.cat != Category.metal:
      ohm_mean = f'{stats.mean(ohms):.3f}'
      ohm_stdev = f'{stats.stdev(ohms):.3f}'
      ohm_min = f'{min(ohms):.3f}'
      ohm_max = f'{max(ohms):.3f}'
      print( m.cat.name, ohm_mean, ohm_stdev, ohm_min, ohm_max, sep='\t')

    x = np.array(xdata)
    y = np.log10( np.array(ydata) )
    #breakpoint()
    self.ax.scatter(x,y, color=plotcolor, s=64)
    #self.ax.plot(x,y, marker='o', linewidth=0, color=plotcolor)
    #self.ax.set_yscale('log')
    self.ax.get_yaxis().set_ticks( [-1,0,1,2,3,4,5,6] )
    self.ax.set_yticklabels([0.1, 1, 10, 100, '1K', '10K', '100K', '1M'])

  def display( self ):
    plt.savefig('out.png', dpi=300)
    plt.show()

  def trace_resistance_vs_width( self, trace, mlist, plotcolor, title='Resistances of Trace' ):
    if self.begin:
      tr_units = symOmega 
      self.ax.set_title(title)
      self.ax.set_xlabel('Width in mm')
      self.ax.grid(True, which='major', axis='y')
      self.ax.set_xlim(0.9, 110)
      self.ax.set_ylabel('Trace Resistance in ' + tr_units)
      self.ax.grid(True, which='both', axis='x')
      self.begin = False

    if mlist is None: return
    xdata = []
    ydata = []
    index = [ m.index for m in mlist ]
    ohms = [] 
    for m in mlist:
      for br in [ m.r_bulk.valmin, m.r_bulk.valmax ]:
        thlist = divide_interval( m.thickness, 10 )
        for th in thlist:
          sr = calc_sr_units( br.magnitude, th)
          tr = (sr * trace.squares).to(u.ohms);
          xdata.append( trace.width.magnitude )
          ydata.append( tr.magnitude )
          ohms.append( tr.magnitude )

    x = np.array(xdata)
    y = np.log10( np.array(ydata) )
    self.ax.set_xscale('log')
    self.ax.scatter(x,y, color=plotcolor, s=64)
    self.ax.get_yaxis().set_ticks( [1, 2,3,4,5,6] )
    self.ax.set_yticklabels([10, 100, '1K', '10K', '100K', '1M'])

  def display( self ):
    plt.savefig('out.png', dpi=300)
    plt.show()


def plot3d():
  plot = Plot3D( scatter=False, wireframe=False, trisurface=True)
  plot.sheet_resistance( bymetals, 'gold' )
  plot.sheet_resistance( byscreen, 'cyan' )
  plot.sheet_resistance( byflexo, 'purple' )
  plot.sheet_resistance( byinkjet, 'black' )
  plot.sheet_resistance( byaerosol, 'orange' )
  plot.display()


def plot2d_sheet_resistance( units = 'mOhms/Sq' ):
  plot = Plot2D( scatter=True)
  #plot.sheet_resistance( bymetals, 'gold' )
  plot.sheet_resistance( [ byname['copper'] ], 'gold', units )
  plot.sheet_resistance( byflexo, 'purple', units )
  plot.sheet_resistance( byinkjet, 'black', units )
  plot.sheet_resistance( byscreen, 'cyan', units )
  plot.sheet_resistance( byaerosol, 'orange', units )
  plot.sheet_resistance( bycarbon, 'gray', units )
  # plot.ax.legend( [ 
  #   'copper', 
  #   Catname[Category.flexo], 
  #   Catname[Category.inkjet],
  #   Catname[Category.screen],
  #   Catname[Category.aerosol] ] )
  plot.display()

def plot2d_bulk_resistivity():
  plot = Plot2D( scatter=True)
  plot.bulk_resistivity( bymetals, 'gold' )
  plot.bulk_resistivity( byflexo, 'purple' )
  plot.bulk_resistivity( byinkjet, 'black' )
  plot.bulk_resistivity( byscreen, 'cyan' )
  plot.bulk_resistivity( byaerosol, 'orange' )
  # plot.ax.legend( [ 
  #   Catname[Category.metal], 
  #   Catname[Category.flexo], 
  #   Catname[Category.inkjet],
  #   Catname[Category.screen],
  #   Catname[Category.aerosol] ] )
  plot.display()

def plot2d_thickness():
  plot = Plot2D( scatter=True)
  plot.thickness( [ byname['copper'] ], 'gold' )
  #plot.thickness( bymetals, 'gold' )
  plot.thickness( byflexo, 'purple' )
  plot.thickness( byinkjet, 'black' )
  plot.thickness( byscreen, 'cyan' )
  plot.thickness( byaerosol, 'orange' )
  # plot.ax.legend( [ 
  #   'copper', Catname[Category.flexo],
  #   Catname[Category.inkjet],
  #   Catname[Category.screen], 
  #   Catname[Category.aerosol] 
  #   ] )
  plot.display()

def plot2d_trace_resistance():
  signal_trace = Trace( 3*u.inch, 8*u.milliinch, 1.4*u.milliinch)
  power_trace = Trace( 2*u.inch, 100*u.milliinch, 1.4*u.milliinch)
  heater_trace = Trace( 2*u.inch, 1*u.cm, 1.4*u.milliinch)
  trace = heater_trace
  #title = 'Power Trace Resistance for 100 mils x 2 inch x 1 oz Cu'
  title = 'Heater Trace Resistance for 1 cm x 2 inch x 1 oz Cu'
  plot = Plot2D( scatter=True)
  plot.trace_resistance( trace, [ byname['copper'] ], 'gold', title )
  #plot.trace_resistance( trace, bymetals, 'gold' )
  plot.trace_resistance( trace, byflexo, 'purple', title )
  plot.trace_resistance( trace, byinkjet, 'black', title )
  plot.trace_resistance( trace, byscreen, 'cyan', title )
  plot.trace_resistance( trace, byaerosol, 'orange', title )
  plot.trace_resistance( trace, bycarbon, 'gray', title )
  # plot.ax.legend( [ 
  #   'copper', Catname[Category.flexo],
  #   Catname[Category.inkjet],
  #   Catname[Category.screen], 
  #   Catname[Category.aerosol] 
  #   ] )
  plot.display()

def plot2d_carbon_resistance():
  traces = []
  # Note: only length and width are used
  #for w in [ 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100 ]: # millimeters
  for w in [ 1, 2, 5, 10, 20, 50, 100 ]: # millimeters
    traces.append( Trace( 2*u.inch, w*u.mm, 1.4*u.milliinch) )
  #title = 'Power Trace Resistance for 100 mils x 2 inch x 1 oz Cu'
  title = 'Heater 2-inch Trace Resistances vs Width'
  plot = Plot2D( scatter=True )
  for t in traces:
    plot.trace_resistance_vs_width( t, bycarbon, 'gray', title )
  # plot.ax.legend( [ 
  #   'copper', Catname[Category.flexo],
  #   Catname[Category.inkjet],
  #   Catname[Category.screen], 
  #   Catname[Category.aerosol] 
  #   ] )
  plot.display()

#plot2d_trace_resistance()
#plot2d_sheet_resistance( units = 'Ohms/Sq' )
plot2d_carbon_resistance()

