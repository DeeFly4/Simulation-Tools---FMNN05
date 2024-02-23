from assimulo.explicit_ode import Explicit_ODE
from assimulo.problem import Explicit_Problem
from assimulo.ode import *
import numpy as np
from numpy import hstack
from numpy.linalg import inv

import matplotlib.pyplot as mpl

class Explicit_Problem_2nd(Explicit_Problem):
	def __init__(self, M, C, K, f, u0, up0, t0):
		self.a = -np.divide(K, M)
		self.b = -np.divide(C, M)

		self.u0 = u0
		self.up0 = up0
		self.t0 = t0

		self.M = M
		self.C = C
		self.K = K
		self.f = f
		Explicit_Problem.__init__(self, self.rhs, hstack((self.u0, self.up0)), t0)

	def rhs(self, t, y):
		u = y[0:len(y)//2]
		up = y[len(y)//2:len(y)]

		y1dot = up
		y2dot = self.a*u + self.b*up + self.f(t) / self.M

		return hstack((y1dot, y2dot))

class Explicit_ODE_2nd(Explicit_ODE):
	def __init__(self, problem):
		Explicit_ODE.__init__(self, problem)
		self.M = problem.M
		self.C = problem.C
		self.K = problem.K
		self.f = problem.f
		self.u0 = problem.u0
		self.up0 = problem.up0
		self.t0 = problem.t0

class Newmark(Explicit_ODE_2nd):
	Beta = 1/2
	gamma = 1/4
	h = 1e-3
	
	def __init__(self, problem):
		Explicit_ODE_2nd.__init__(self, problem)
		self.M = np.diag(self.M)
		self.C = np.diag(self.C)
		self.K = np.diag(self.K)
  
		self.up = self.up0
		
		self.invA = inv(self.M / (self.Beta*self.h**2) + self.gamma*self.C / (self.Beta*self.h) + self.K)

 
	def integrate(self, t, u, up, tf, opts):
		h = min(self.h, abs(tf-t))
		upp = inv(self.M)@self.f(0) - self.C@up - self.K@u

		tres = []
		ures = []
  
		while (t < tf):
			t, u, up, upp = self.step(t, u, up, upp, h)

			tres.append(t)
			ures.append(u.copy())

			h = min(self.h, abs(tf-t))

		return ID_PY_OK, tres, ures
	
	def simulate(self, tf):
		flag, t, u = self.integrate(self.t0, self.u0, self.up0, tf, opts=None)
		return t, u
 
	def step(self, t, u, up, upp, h):
		bh = self.Beta*h
		bh2 = self.Beta*h**2
		inv2bmo = 1/(2*self.Beta) - 1
		omgb = 1 - self.gamma/self.Beta
		omg2b = 1 - self.gamma/(2*self.Beta)
  
		t_next = t+h

		Bn = self.f(t_next) + self.M @ (u/bh2 + up/bh + upp*inv2bmo) + self.C @ (self.gamma*u/bh - up*omgb - h*upp*omg2b)
		
		u_next = self.invA @ Bn
		up_next = self.gamma*(u_next - u)/bh + up*omgb + h*upp*omg2b
		upp_next = (u_next - u)/bh2 - up/bh - upp*inv2bmo
  
		return t_next, u_next, up_next, upp_next