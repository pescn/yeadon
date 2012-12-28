'''Solid objects are used by the segment module. A solid has a position, and
orientation (defined by a rotation matrix). This module also contains the
class definition for stadium objects, which are used to construct
stadiumsolid solids. The solid class has two children: the stadiumsolid and
semiellipsoid classes.

'''
import textwrap
import warnings

import numpy as np

try:
    from mayavi import mlab
except ImportError:
    print "Yeadon failed to import mayavi. It is possible that you do" \
          " not have this package. This is fine, it just means that you " \
          "cannot use the draw_mayavi() member functions."
try:
    import visual as vis
except ImportError:
    # TODO: Make this a warning
    print "Yeadon failed to import python-visual. It is possible that you do" \
          " not have this package. This is fine, it just means that you " \
          "cannot use the draw_visual() member functions."

import inertia


class Stadium(object):
    '''Stadium, the 2D shape.

    '''
    validStadiaLabels = {
        'Ls0': 'hip joint centre',
        'Ls1': 'umbilicus',
        'Ls2': 'lowest front rib',
        'Ls3': 'nipple',
        'Ls4': 'shoulder joint centre',
        'Ls5': 'acromion',
        'Ls6': 'beneath nose',
        'Ls7': 'above ear',
        'La0': 'shoulder joint centre',
        'La1': 'mid-arm',
        'La2': 'lowest front rib',
        'La3': 'nipple',
        'La4': 'wrist joint centre',
        'La5': 'acromion',
        'La6': 'knuckles',
        'La7': 'fingernails',
        'Lb0': 'shoulder joint centre',
        'Lb1': 'mid-arm',
        'Lb2': 'lowest front rib',
        'Lb3': 'nipple',
        'Lb4': 'wrist joint centre',
        'Lb5': 'acromion',
        'Lb6': 'knuckles',
        'Lb7': 'fingernails',
        'Lj0': 'hip joint centre',
        'Lj1': 'crotch',
        'Lj2': 'mid-thigh',
        'Lj3': 'knee joint centre',
        'Lj4': 'maximum calf perimeter',
        'Lj5': 'ankle joint centre',
        'Lj6': 'heel',
        'Lj7': 'arch',
        'Lj8': 'ball',
        'Lj9': 'toe nails',
        'Lk0': 'hip joint centre',
        'Lk1': 'crotch',
        'Lk2': 'mid-thigh',
        'Lk3': 'knee joint centre',
        'Lk4': 'maximum calf perimeter',
        'Lk5': 'ankle joint centre',
        'Lk6': 'heel',
        'Lk7': 'arch',
        'Lk8': 'ball',
        'Lk9': 'toe nails'}

    def __init__(self, label, inID, in1, in2=None, alignment='ML'):
        '''Defines a 2D stadium shape and checks inputs for errors. A stadium,
        described in Yeadon 1990-ii, is defined by two parameters.  Stadia can
        depracate to circles if their "thickness" is 0.

        Parameters
        ----------
        label : str
            Name of the stadium level, according to Yeadon 1990-ii.
        inID : str
            Identifies the type of information for the next two inputs.
            'perimwidth' for perimeter and width input, 'depthwidth' for
            depth and width input, 'perimeter' or 'radius' for a circle,
            'thicknessradius' for thickness and radius input.
        in1 : float
            Either perimeter, depth, or thickness, as determined by inID
        in2 : float
            Either width, or radius, as determined by inID
        alignment = 'ML' : str
            Identifies the long direction of the stadium. 'ML' stands for
            medio-lateral. Aleternatively, 'AP' (anterior-posterior) can be
            supplied. The only 'AP' stadiums should be at the heels.

        '''
        if label == 'Ls5: acromion/bottom of neck':
            self.label = label
        elif label in [lab + ': ' + desc for lab, desc in
                self.validStadiaLabels.items()]:
            self.label = label
        else:
            raise ValueError("'{}' is not a valid label.".format(label))

        if inID == 'perimwidth':
            self.perimeter = in1
            self.width = in2
            self.thickness = ((np.pi * self.width - self.perimeter) /
                          (2.0 * np.pi - 4.0))
            self.radius = ((self.perimeter - 2.0 * self.width)  /
                           (2.0 * np.pi - 4.0))
        elif inID == 'depthwidth':
            self.width = in2
            self.perimeter = 2.0 * in2 + (np.pi - 2.0) * in1
            self.thickness = ((np.pi * self.width - self.perimeter) /
                          (2.0 * np.pi - 4.0))
            self.radius = (self.perimeter - 2.0 * self.width) / (2.0 * np.pi - 4.0)
        elif inID == 'perimeter':
            self._set_as_circle(in1 / (2.0 * np.pi))
        elif inID == 'radius':
            self._set_as_circle(in1)
        elif inID == 'thicknessradius':
            self.thickness = in1
            self.radius = in2
            self.perimeter = 4.0 * self.thickness + 2.0 * np.pi * self.radius
            self.width = 2.0 * self.thickness + 2.0 * self.radius
        else:
            raise ValueError("Error: stadium " + self.label +
                " not defined properly, " + inID + " is not valid. You must " +
                "use inID= perimwidth, depthwidth, perimeter, or radius.")
        if self.radius <= 0 or self.thickness < 0:
            warnings.warn(textwrap.dedent("""Error: stadium '{}' is defined
                incorrectly, r must be positive and t must be nonnegative. r =
                {} and t = {} . This means that 2 < perimeter/width < pi.
                Currently, this ratio is {}.""").format(self.label, self.radius,
                self.thickness, self.perimeter / self.width))
            if inID == 'perimwidth':
                self._set_as_circle(in1 / (2.0 * np.pi))
                print "Fix: stadium set as circle with perimeter as given."
            elif inID == 'depthwidth':
                self._set_as_circle(2 * in2)
                print "Fix: stadium set as circle with diameter of given width."
        if alignment != 'AP' and alignment != 'ML':
            raise ValueError("Error: stadium " + self.label +
                " alignment is not valid, must be either AP or ML")
        else:
            self.alignment = alignment
    
    def _set_as_circle(self, radius):
        """Sets radius, perimeter, thickness, and width if thickness is 0."""
        self.radius = radius
        self.perimeter = 2.0 * np.pi * self.radius
        self.thickness = 0.0
        self.width = self.perimeter / np.pi

    def plot(self, ax, c):
        '''Plots the 2D stadium on 3D axes using matplotlib and its Axes3D
        class.

        Parameters
        ----------
        ax : Axes3D object
            Axis object from the matplotlib library.
        c : str
            Color, as a word. e.g. 'red'

        '''
        theta = [np.linspace(0.0, np.pi / 2.0, 5)]
        x = self.thickness + self.radius * np.cos(theta);
        y = self.radius * np.sin(theta);
        xrev = x[:, ::-1]
        yrev = y[:, ::-1]
        X2 = np.concatenate( (x, -xrev, -x, xrev ), axis = 1)
        Y2 = np.concatenate( (y, yrev, -y, -yrev ), axis = 1)
        X3 = np.concatenate( (X2, np.nan * X2), axis = 0)
        Y3 = np.concatenate( (Y2, np.nan * Y2), axis = 0)
        ax.plot_surface(X3, Y3, np.zeros((2, 20)), color=c, alpha=0.5)

class Solid(object):
    '''Solid. Has two subclasses, stadiumsolid and semiellipsoid. This base
    class manages setting orientation, and calculating properties.

    '''
    # Transparency for plotting.
    alpha = .5

    def __init__(self, label, density, height):
        '''Defines a solid. This is a base class. Sets the alpha value to
        be used for drawing with matplotlib.

        Parameters
        ----------
        label : str
            Name of the solid
        density : float
            In units (kg/m^3), used to calculate the solid's mass
        height : float
            Distance from bottom to top of the solid

        '''
        #TODO: Check for valid labels
        self.label = label
        #TODO: Check that these two are floats
        self.density = density
        self.height = height
        self.relInertia = np.zeros((3, 3)) # this gets set in subclasses
        self.Mass = 0.0
        self.relCOM = np.array([[0.0], [0.0], [0.0]])

    def set_orientation(self, pos, rot_mat):
        '''Sets the position, rotation matrix of the solid, and calculates
        the "absolute" properties (center of mass, and inertia tensor) of the
        solid.

        Parameters
        ----------
        pos : np.array (3,1)
            Position of the base of the solid in the absolute fixed coordinates
            of the human.
        rot_mat : np.matrix (3,3)
            Orientation of solid, with respect to the fixed coordinate system.

        '''
        self.pos = pos
        self.rot_mat = rot_mat
        self.endpos = self.pos + (self.height * self.rot_mat *
                                  np.array([[0], [0], [1]]))
        self.calc_properties()

    def calc_properties(self):
        '''Sets the center of mass and inertia of the solid, both with respect
        to the fixed human frame.

        '''
        try:
            try:
                self.COM = self.pos + self.rot_mat * self.relCOM
            except AttributeError as err:
                err.message = err.message + \
                    '. You must set the orientation before attempting ' + \
                    'to calculate the properties.'
                raise
        except AttributeError as e:
            print(e.message)

        self.Inertia = inertia.rotate3_inertia(self.rot_mat, self.relInertia)

    def print_properties(self):
        '''Prints the mass, center of mass (local and absolute), and inertia
        tensor (local and absolute) of the solid.

        '''
        print self.label, "properties:\n"
        print "Mass (kg):", self.Mass,"\n"
        print "COM in local solid's frame (m):\n", self.relCOM,"\n"
        print "COM in fixed human frame (m):\n", self.COM,"\n"
        print "Inertia tensor in solid's frame about local solid's",\
               "COM (kg-m^2):\n", self.relInertia,"\n"
        print "Inertia tensor in fixed human frame about local solid's",\
               "COM (kg-m^2):\n", self.Inertia,"\n"

    def draw(self, ax, c):
        #TODO: Make into warning
        print "Cannot draw from base class solid, use a subclass like StadiumSolid or SemiEllipsoidSolid)."

class StadiumSolid(Solid):
    '''Stadium solid. Derived from the solid class.

    '''
    def __init__(self,label,density,stadium0,stadium1,height):
        '''Defines a stadium solid object. Creates its base object, and
        calculates relative/local inertia properties.

        Parameters
        ----------
        label : str
            Name of the solid.
        density : float
            Density of the solid (kg/m^3).
        stadium0 : :py:class:`Stadium`
            Lower stadium of the stadium solid.
        stadium1 : :py:class:`Stadium`
            Upper stadium of the stadium solid.
        height : float
            Distance between the lower and upper stadia.

        '''
        super(StadiumSolid, self).__init__(label,density,height)
        self.stads = [stadium0,stadium1]
        self.alignment = 'ML'
        # if either stadium is oriented anterior-posterior,
        # inertia must be rotated, and the plots must be modified
        if (self.stads[0].alignment == 'AP' or
            self.stads[1].alignment == 'AP'):
            self.alignment = 'AP'
        self.calc_rel_properties()

    def calc_rel_properties(self):
        '''Calculates mass, relative center of mass, and relative/local
        inertia, according to formulae in Appendix B of Yeadon 1990-ii. If the
        stadium solid is arranged anterior-posteriorly, the inertia is rotated
        by pi/2 about the z axis.

        '''
        D = self.density
        h = self.height
        r0 = self.stads[0].radius
        t0 = self.stads[0].thickness
        r1 = self.stads[1].radius
        t1 = self.stads[1].thickness
        a = (r1 - r0) / r0
        if (t0 == 0):
            b = 1.0
        else:
            b = (t1 - t0) / t0 # DOES NOT WORK FOR CIRCLES!!!
        self.Mass = D * h * r0 * (4.0 * t0 * self.F1(a,b) +
                                  np.pi * r0 * self.F1(a,a))
        zcom = D * (h**2.0) * (4.0 * r0 * t0 * self.F2(a,b) +
                               np.pi * (r0**2.0) * self.F2(a,a)) / self.Mass
        self.relCOM = np.array([[0.0],[0.0],[zcom]])
        # moments of inertia
        Izcom = D * h * (4.0 * r0 * (t0**3.0) * self.F4(a,b) / 3.0 +
                         np.pi * (r0**2.0) * (t0**2.0) * self.F5(a,b) +
                         4.0 * (r0**3.0) * t0 * self.F4(b,a) +
                         np.pi * (r0**4.0) * self.F4(a,a) * 0.5 )
        Iy = (D * h * (4.0 * r0 * (t0**3.0) * self.F4(a,b) / 3.0 +
                       np.pi * (r0**2.0) * (t0**2.0) * self.F5(a,b) +
                       8.0 * (r0**3.0) * t0*self.F4(b,a) / 3.0 +
                      np.pi * (r0**4.0) * self.F4(a,a) * 0.25) +
              D * (h**3.0) * (4.0 * r0 * t0 * self.F3(a,b) +
                              np.pi * (r0**2.0) * self.F3(a,a)))
        # CAUGHT AN (minor) ERROR IN YEADON'S PAPER HERE
        Iycom = Iy - self.Mass * (zcom**2.0)
        Ix = (D * h * (4.0 * r0 * (t0**3.0) * self.F4(a,b) / 3.0 +
                       np.pi * (r0**4.0) * self.F4(a,a) * 0.25) +
              D * (h**3.0) * (4.0 * r0 * t0 * self.F3(a,b) +
                              np.pi * (r0**2.0) * self.F3(a,a)))
        Ixcom = Ix - self.Mass*(zcom**2.0)
        self.relInertia = np.mat([[Ixcom,0.0,0.0],
                                  [0.0,Iycom,0.0],
                                  [0.0,0.0,Izcom]])
        if self.alignment == 'AP':
            # rearrange to anterior-posterior orientation
            self.relInertia = inertia.rotate3_inertia(
                              inertia.rotate_space_123([0,0,np.pi/2]),self.relInertia)

    def draw(self, ax, c):
        '''Draws stadium solid using matplotlib's mplot3d library. Plotted with
        a non-one value for alpha. Also places the solid's label near the
        center of mass of the solid. Adjusts the plot for solids oriented
        anterior-posteriorly. Plots coordinate axes of the solid at the base of
        the solid.

        Parameters
        ----------
        ax : plt.axes
            Matplotlib axes upon which to draw.
        c : str
            Color (e.g. 'red') to use for drawing the solid

        '''
        X0,Y0,Z0,X0toplot,Y0toplot,Z0toplot = self.make_pos(0)
        X1,Y1,Z1,X1toplot,Y1toplot,Z1toplot = self.make_pos(1)
        for idx in np.arange(X0.size-1):
            Xpts = np.array([[X0[0,idx],X0[0,idx+1]],[X1[0,idx],X1[0,idx+1]]])
            Ypts = np.array([[Y0[0,idx],Y0[0,idx+1]],[Y1[0,idx],Y1[0,idx+1]]])
            Zpts = np.array([[Z0[0,idx],Z0[0,idx+1]],[Z1[0,idx],Z1[0,idx+1]]])
            ax.plot_surface( Xpts, Ypts, Zpts, color=c, alpha=Solid.alpha, edgecolor='');
            if 0:
                if idx == 8:
                    print "IDX IS 8\n",Xpts,'\n',Ypts,'\n',Zpts
                if idx == 9:
                    print "IDX IS 9\n",Xpts,'\n',Ypts,'\n',Zpts
        # draw stad0
        ax.plot_surface( X0toplot, Y0toplot, Z0toplot,
                         color=c, alpha=Solid.alpha)
        # draw stad1
        ax.plot_surface( X1toplot, Y1toplot, Z1toplot,
                         color=c, alpha=Solid.alpha)
        # rotated unit vectors (unit x prime, etc)
        uxp = self.rot_mat * np.array([[1],[0],[0]]) + self.pos
        uyp = self.rot_mat * np.array([[0],[1],[0]]) + self.pos
        uzp = self.rot_mat * np.array([[0],[0],[1]]) + self.pos
        if 0:
            ax.plot( np.array([self.pos[0,0],uxp[0]]),
                     np.array([self.pos[1,0],uxp[1]]),
                     np.array([self.pos[2,0],uxp[2]]),
                     color=(1,0,0,1), linewidth = 2)
            ax.plot( np.array([self.pos[0,0],uyp[0]]),
                     np.array([self.pos[1,0],uyp[1]]),
                     np.array([self.pos[2,0],uyp[2]]),
                     color=(0,1,0,1), linewidth = 2)
            ax.plot( np.array([self.pos[0,0],uzp[0]]),
                     np.array([self.pos[1,0],uzp[1]]),
                     np.array([self.pos[2,0],uzp[2]]),
                     color=(0,0,1,0), linewidth = 2)
        # place solid's text label on the plot
        (labelstring,b,c) = self.label.partition(':')
        ax.text(self.COM[0],self.COM[1],self.COM[2],labelstring)

    def draw_mayavi(self, fig, col):
        '''Draws the stadium in 3D using MayaVi.
        
        Parameters
        ----------
        fig : :py:class:`mayavi.mlab.figure`
            MayaVi figure in which to draw the mesh.
        col : tuple (3,)
            Color as an rgb tuple, with values between 0 and 1.

        '''
        X0,Y0,Z0,X0toplot,Y0toplot,Z0toplot = self.make_pos(0)
        X1,Y1,Z1,X1toplot,Y1toplot,Z1toplot = self.make_pos(1)
        Xpts = np.array(np.concatenate( (X0, X1), axis=0))
        Ypts = np.array(np.concatenate( (Y0, Y1), axis=0))
        Zpts = np.array(np.concatenate( (Z0, Z1), axis=0))
        mlab.mesh(Xpts, Ypts, Zpts, figure=fig, color=col, opacity=Solid.alpha)

    def draw_visual(self, c):
        '''Draws the stadium in 3D in a VPython window. Only one line of code!

        Parameters
        ----------
        c : tuple (3,)
            Color as an rgb tuple, with values between 0 and 1.

        '''
        vis.convex(pos = self.make_pos_visual(), color=c)

    def make_pos_visual(self):
        '''Creates a list of x,y,z points to use for drawing a convex shape in
        VPython (the method yeadon.Solid.draw_visual)

        '''
        N = 10
        pos = []
        for i in [0,1]:
            theta = [np.linspace(0.0,np.pi/2,N)]
            x = self.stads[i].thickness + self.stads[i].radius * np.cos(theta);
            y = self.stads[i].radius * np.sin(theta);
            if self.alignment == 'AP':
                temp = x
                x = y
                y = temp
                del temp
            xrev = x[:, ::-1]
            yrev = y[:, ::-1]
            X = np.concatenate( (x, -xrev, -x, xrev), axis=1)
            Y = np.concatenate( (y, yrev, -y, -yrev), axis=1)
            Z = i*self.height*np.ones((1,N*4))
            POSES = np.concatenate( (X, Y, Z), axis=0)
            POSES = self.rot_mat * POSES
            X,Y,Z = np.vsplit(POSES,3)
            X = X + self.pos[0]
            Y = Y + self.pos[1]
            Z = Z + self.pos[2]
            POSES = np.concatenate( (X, Y, Z), axis=0)
            for j in np.arange(N*4):
                pos.append( (POSES[0,j], POSES[1,j], POSES[2,j]) )
        return pos

    def make_pos(self,i):
        '''Generates coordinates to be used for 3D visualization purposes.

        '''
        theta = [np.linspace(0.0,np.pi/2,5)]
        x = self.stads[i].thickness + self.stads[i].radius * np.cos(theta);
        y = self.stads[i].radius * np.sin(theta);
        if self.alignment == 'AP':
            temp = x
            x = y
            y = temp
            del temp
        xrev = x[:, ::-1]
        yrev = y[:, ::-1]
        X = np.concatenate( (x, -xrev, -x, xrev), axis=1)
        Y = np.concatenate( (y, yrev, -y, -yrev), axis=1)
        Z = i*self.height*np.ones((1,20))
        POSES = np.concatenate( (X, Y, Z), axis=0)
        POSES = self.rot_mat * POSES
        X,Y,Z = np.vsplit(POSES,3)
        X = X + self.pos[0]
        Y = Y + self.pos[1]
        Z = Z + self.pos[2]
        Xtoplot = np.array(np.concatenate((X, np.nan*X)))
        Ytoplot = np.array(np.concatenate((Y, np.nan*Y)))
        Ztoplot = np.array(np.concatenate((Z, np.nan*Z)))
        return X,Y,Z,Xtoplot,Ytoplot,Ztoplot

    def F1(self,a,b):
        '''Integration term. See Yeadon 1990-ii Appendix 2.'''
        return 1.0 + (a + b) * 0.5 + a * b / 3.0
    def F2(self,a,b):
        '''Integration term. See Yeadon 1990-ii Appendix 2.'''
        return 0.5 + (a + b) / 3.0 + a * b * 0.25
    def F3(self,a,b):
        '''Integration term. See Yeadon 1990-ii Appendix 2.'''
        return 1.0/3.0 + (a + b) / 4.0 + a * b *0.2
    def F4(self,a,b):
        '''Integration term. See Yeadon 1990-ii Appendix 2.'''
        return (1.0 + (a + 3.0 * b) * 0.5 + (a * b + b**2.0) +
                      (3.0 * a * b**2.0 + b**3.0) * 0.25 + a * (b**3.0) * 0.2)
    def F5(self,a,b):
        '''Integration term. See Yeadon 1990-ii Appendix 2.'''
        return (1.0 + (a + b) + (a**2.0 + 4.0 * a * b + b**2.0) / 3.0 +
                       a * b * (a + b) * 0.5 + (a**2.0) * (b**2.0) * 0.2)

class Semiellipsoid(Solid):
    '''Semiellipsoid.
    '''
    def __init__(self,label,density,baseperim,height):
        '''Defines a semiellipsoid (solid) object. Creates its base object, and
        calculates relative/local inertia properties. The base is circular (its
        height axis is pointed upwards), so only 2 parameters are needed to
        define the semiellipsoid.

        Parameters
        ----------
        label : str
            Name of the solid.
        density : float
            Density of the solid (kg/m^3).
        baseperimeter : float
            The base is circular.
        height : float
            The remaining minor axis.

        '''
        super(Semiellipsoid, self).__init__(label,density,height)
        self.baseperimeter = baseperim
        self.radius = self.baseperimeter/(2.0*np.pi)

        self.calc_rel_properties()

    def calc_rel_properties(self):
        '''Calculates mass, relative center of mass, and relative/local
        inertia, according to somewhat commonly availble formulae.

        '''
        D = self.density
        r = self.radius
        h = self.height
        self.Mass = D * 2.0/3.0 * np.pi * (r**2) * h
        self.relCOM = np.array([[0.0],[0.0],[3.0/8.0 * h]])
        Izcom = D * 4.0/15.0 * np.pi * (r**4.0) * h
        Iycom = D * np.pi * (2.0/15.0 * (r**2.0) * h * (r**2.0 + h**2.0) -
            3.0/32.0 * (r**2.0) * (h**3.0))
        Ixcom = Iycom
        self.relInertia = np.mat([[Ixcom,0.0,0.0],
                                  [0.0,Iycom,0.0],
                                  [0.0,0.0,Izcom]])

    def draw(self,ax,c):
        '''Draws semiellipsoid using matplotlib's mplot3d library. Plotted with
        a non-one value for alpha. Also places the solid's label near the
        center of mass of the solid. Plots coordinate axes of the solid at the
        base of the solid. Code is modified from matplotlib documentation for
        mplot3d.

        Parameters
        ----------
        ax : plt.Axes3D
            Matplotlib axes to draw upon.
         c : str
            Color (e.g. 'red').

        '''
        x, y, z = self._make_pos()
        ax.plot_surface( x, y, z, rstride=4, cstride=4,
                         color=c, alpha=Solid.alpha , edgecolor='')
        (labelstring,b,c) = self.label.partition(':')
        ax.text(self.COM[0],self.COM[1],self.COM[2],labelstring)

    def draw_mayavi(self, fig, col):
        '''Draws the semiellipsoid in 3D using MayaVi.
        
        Parameters
        ----------
        fig : :py:class:`mayavi.mlab.figure`
            MayaVi figure in which to draw the mesh.
        col : tuple (3,)
            Color as an rgb tuple, with values between 0 and 1.

        '''
        x, y, z = self._make_pos()
        mlab.mesh(x, y, z, figure=fig, color=col, opacity=Solid.alpha)

    def draw_visual(self, c):
        '''Draws an ellipse in VPython. Ideally would only draw the top half of
        the ellipse, but draws the entire ellipse. This disadvantage makes it
        seem as if the head is more "round" than it actually is.

        '''
        ax = self.rot_mat * np.array([[0],[0],[1]])
        vis.ellipsoid(pos = (self.pos[0,0],self.pos[1,0],self.pos[2,0]),
                         axis = (ax[0,0],ax[1,0],ax[2,0]),
                         length=self.height,
                         height=self.radius*2,
                         width=self.radius*2,
                         color=c)
    def _make_pos(self):
        '''Generates coordinates to be used for 3D visualization purposes.

        '''
        N = 30
        u = np.linspace(0, 2.0 * np.pi, N)
        v = np.linspace(0, np.pi / 2.0, N)
        x = self.radius * np.outer(np.cos(u), np.sin(v))
        y = self.radius * np.outer(np.sin(u), np.sin(v))
        z = self.height * np.outer(np.ones(np.size(u)), np.cos(v))
        for i in np.arange(N):
            for j in np.arange(N):
                POS = np.array([[x[i,j]],[y[i,j]],[z[i,j]]])
                POS = self.rot_mat * POS
                x[i,j] = POS[0,0]
                y[i,j] = POS[1,0]
                z[i,j] = POS[2,0]
        x = self.pos[0,0] + x
        y = self.pos[1,0] + y
        z = self.pos[2,0] + z
        return x, y, z

